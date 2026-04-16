from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Pool:
    address: str
    dex: str  # uniswap_v3, aerodrome, baseswap, sushiswap
    token_a: str
    token_b: str
    price: float  # token_b per token_a
    liquidity: float
    fee: float  # e.g. 0.003 for 0.3%
    tick_spacing: Optional[int] = None
    sqrt_price_x96: Optional[int] = None


@dataclass
class PriceQuote:
    token_a: str
    token_b: str
    dex: str
    price: float
    pool_address: str
    liquidity: float
    fee: float
    timestamp: float = 0.0


@dataclass
class SwapRoute:
    token_in: str
    token_out: str
    amount_in: float
    amount_out: float
    path: list[str]  # token addresses
    pools: list[str]  # pool addresses
    dexes: list[str]
    gas_estimate: int = 150000
    price_impact: float = 0.0
    effective_price: float = 0.0


@dataclass
class Opportunity:
    token_a: str
    token_b: str
    buy_dex: str
    sell_dex: str
    buy_price: float
    sell_price: float
    spread_pct: float
    estimated_profit_pct: float
    buy_pool: str = ""
    sell_pool: str = ""


@dataclass
class LiquidityDepth:
    pool_address: str
    dex: str
    token_a: str
    token_b: str
    current_price: float
    bids: list[tuple[float, float]] = field(default_factory=list)  # (price, liquidity)
    asks: list[tuple[float, float]] = field(default_factory=list)
