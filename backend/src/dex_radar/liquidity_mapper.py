import math
from .models import Pool, LiquidityDepth

DEPTH_LEVELS = 10
PRICE_RANGE_PCT = 0.05  # ±5% around current price


def compute_liquidity_depth(pool: Pool) -> LiquidityDepth:
    current = pool.price
    step = current * PRICE_RANGE_PCT / DEPTH_LEVELS

    bids = []
    asks = []
    for i in range(1, DEPTH_LEVELS + 1):
        bid_price = current - i * step
        ask_price = current + i * step
        if bid_price <= 0:
            continue
        # Approximate: liquidity decreases away from current price
        decay = math.exp(-0.3 * i)
        liq = pool.liquidity * decay
        bids.append((round(bid_price, 6), round(liq, 2)))
        asks.append((round(ask_price, 6), round(liq, 2)))

    return LiquidityDepth(
        pool_address=pool.address,
        dex=pool.dex,
        token_a=pool.token_a,
        token_b=pool.token_b,
        current_price=current,
        bids=bids,
        asks=asks,
    )


def map_all_liquidity(pools: list[Pool]) -> list[LiquidityDepth]:
    return [compute_liquidity_depth(p) for p in pools]
