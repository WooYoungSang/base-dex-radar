from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .liquidity_mapper import compute_liquidity_depth
from .models import Pool
from .opportunity_detector import find_opportunities
from .path_finder import find_best_route
from .pool_reader import fetch_all_pools
from .price_engine import build_price_quotes, compare_prices
from .schemas import (
    GasResponse,
    HealthResponse,
    LiquidityLevel,
    LiquidityResponse,
    OpportunityResponse,
    PriceResponse,
    PricesResponse,
    RouteResponse,
)

_pools: list[Pool] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _pools
    _pools = await fetch_all_pools(use_rpc=False)
    yield


app = FastAPI(
    title="Base DEX Radar API",
    description="AI-powered DEX intelligence platform for Base — powered by KAIROS CUDA PathFinder",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _require_pools() -> list[Pool]:
    if not _pools:
        raise HTTPException(status_code=503, detail="Pool data not loaded yet")
    return _pools


# --- Rate limiting stub ---
async def _check_rate_limit(x_api_key: Annotated[str | None, Header()] = None) -> None:
    pass  # stub: enforce in production via Redis


@app.get("/api/health", response_model=HealthResponse, tags=["meta"])
async def health():
    return HealthResponse(status="ok", version="0.1.0", pools_loaded=len(_pools))


@app.get("/api/prices", response_model=PricesResponse, tags=["prices"])
async def get_prices(
    token_a: str = Query(..., description="Token A symbol, e.g. ETH"),
    token_b: str = Query(..., description="Token B symbol, e.g. USDC"),
    x_api_key: Annotated[str | None, Header()] = None,
):
    pools = _require_pools()
    quotes = build_price_quotes(pools)
    filtered = compare_prices(quotes, token_a.upper(), token_b.upper())
    if not filtered:
        raise HTTPException(status_code=404, detail=f"No pools found for {token_a}/{token_b}")
    return PricesResponse(
        pair=f"{token_a.upper()}/{token_b.upper()}",
        quotes=[
            PriceResponse(
                token_a=q.token_a,
                token_b=q.token_b,
                dex=q.dex,
                price=q.price,
                pool_address=q.pool_address,
                liquidity=q.liquidity,
                fee=q.fee,
                timestamp=q.timestamp,
            )
            for q in filtered
        ],
    )


@app.get("/api/route", response_model=RouteResponse, tags=["routing"])
async def get_route(
    token_a: str = Query(..., description="Input token symbol, e.g. ETH"),
    token_b: str = Query(..., description="Output token symbol, e.g. USDC"),
    amount: float = Query(1.0, description="Amount of token_a to swap"),
    x_api_key: Annotated[str | None, Header()] = None,
):
    pools = _require_pools()
    route = find_best_route(pools, token_a.upper(), token_b.upper(), amount)
    if route is None:
        raise HTTPException(status_code=404, detail=f"No route found for {token_a} → {token_b}")
    return RouteResponse(
        token_in=route.token_in,
        token_out=route.token_out,
        amount_in=route.amount_in,
        amount_out=route.amount_out,
        path=route.path,
        pools=route.pools,
        dexes=route.dexes,
        gas_estimate=route.gas_estimate,
        price_impact=route.price_impact,
        effective_price=route.effective_price,
    )


@app.get("/api/liquidity/{pool_address}", response_model=LiquidityResponse, tags=["liquidity"])
async def get_liquidity(
    pool_address: str,
    x_api_key: Annotated[str | None, Header()] = None,
):
    pools = _require_pools()
    pool = next((p for p in pools if p.address.lower() == pool_address.lower()), None)
    if pool is None:
        raise HTTPException(status_code=404, detail=f"Pool {pool_address} not found")
    depth = compute_liquidity_depth(pool)
    return LiquidityResponse(
        pool_address=depth.pool_address,
        dex=depth.dex,
        token_a=depth.token_a,
        token_b=depth.token_b,
        current_price=depth.current_price,
        bids=[LiquidityLevel(price=px, liquidity=liq) for px, liq in depth.bids],
        asks=[LiquidityLevel(price=px, liquidity=liq) for px, liq in depth.asks],
    )


@app.get("/api/gas", response_model=GasResponse, tags=["gas"])
async def get_gas(x_api_key: Annotated[str | None, Header()] = None):
    base_fee = 0.002  # mock: 0.002 gwei on Base L2
    priority = 0.001
    eth_price = 3450.0
    gas_units = 150_000
    cost_eth = (base_fee + priority) * 1e-9 * gas_units
    cost_usd = cost_eth * eth_price
    return GasResponse(
        base_fee_gwei=base_fee,
        priority_fee_gwei=priority,
        estimated_swap_usd=round(cost_usd, 4),
        source="mock",
    )


@app.get("/api/opportunities", response_model=list[OpportunityResponse], tags=["opportunities"])
async def get_opportunities(x_api_key: Annotated[str | None, Header()] = None):
    pools = _require_pools()
    opps = find_opportunities(pools)
    return [
        OpportunityResponse(
            token_a=o.token_a,
            token_b=o.token_b,
            buy_dex=o.buy_dex,
            sell_dex=o.sell_dex,
            buy_price=o.buy_price,
            sell_price=o.sell_price,
            spread_pct=o.spread_pct,
            estimated_profit_pct=o.estimated_profit_pct,
            buy_pool=o.buy_pool,
            sell_pool=o.sell_pool,
        )
        for o in opps
    ]
