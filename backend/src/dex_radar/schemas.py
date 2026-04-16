from pydantic import BaseModel


class PriceResponse(BaseModel):
    token_a: str
    token_b: str
    dex: str
    price: float
    pool_address: str
    liquidity: float
    fee: float
    timestamp: float


class PricesResponse(BaseModel):
    quotes: list[PriceResponse]
    pair: str


class RouteHop(BaseModel):
    pool_address: str
    dex: str
    token_in: str
    token_out: str


class RouteResponse(BaseModel):
    token_in: str
    token_out: str
    amount_in: float
    amount_out: float
    path: list[str]
    pools: list[str]
    dexes: list[str]
    gas_estimate: int
    price_impact: float
    effective_price: float


class LiquidityLevel(BaseModel):
    price: float
    liquidity: float


class LiquidityResponse(BaseModel):
    pool_address: str
    dex: str
    token_a: str
    token_b: str
    current_price: float
    bids: list[LiquidityLevel]
    asks: list[LiquidityLevel]


class GasResponse(BaseModel):
    base_fee_gwei: float
    priority_fee_gwei: float
    estimated_swap_usd: float
    source: str = "mock"


class OpportunityResponse(BaseModel):
    token_a: str
    token_b: str
    buy_dex: str
    sell_dex: str
    buy_price: float
    sell_price: float
    spread_pct: float
    estimated_profit_pct: float
    buy_pool: str
    sell_pool: str


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    pools_loaded: int = 0
