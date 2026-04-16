import time
from typing import Optional

from .models import Pool, PriceQuote


def build_price_quotes(pools: list[Pool], timestamp: Optional[float] = None) -> list[PriceQuote]:
    ts = timestamp if timestamp is not None else time.time()
    quotes = []
    for pool in pools:
        quotes.append(
            PriceQuote(
                token_a=pool.token_a,
                token_b=pool.token_b,
                dex=pool.dex,
                price=pool.price,
                pool_address=pool.address,
                liquidity=pool.liquidity,
                fee=pool.fee,
                timestamp=ts,
            )
        )
    return quotes


def compare_prices(
    quotes: list[PriceQuote], token_a: str, token_b: str
) -> list[PriceQuote]:
    return [
        q for q in quotes
        if (q.token_a == token_a and q.token_b == token_b)
        or (q.token_a == token_b and q.token_b == token_a)
    ]


def best_buy_quote(quotes: list[PriceQuote], token_a: str, token_b: str) -> Optional[PriceQuote]:
    """Lowest price to buy token_b with token_a (lowest token_b per token_a = cheapest buy)."""
    relevant = compare_prices(quotes, token_a, token_b)
    if not relevant:
        return None
    # For buying token_b with token_a, lower price means cheaper
    return min(relevant, key=lambda q: q.price if q.token_a == token_a else 1.0 / q.price)


def best_sell_quote(quotes: list[PriceQuote], token_a: str, token_b: str) -> Optional[PriceQuote]:
    """Highest price when selling token_a for token_b."""
    relevant = compare_prices(quotes, token_a, token_b)
    if not relevant:
        return None
    return max(relevant, key=lambda q: q.price if q.token_a == token_a else 1.0 / q.price)


def price_spread(quotes: list[PriceQuote], token_a: str, token_b: str) -> float:
    """Returns spread as a fraction (e.g. 0.005 = 0.5%)."""
    relevant = [
        q.price for q in quotes if q.token_a == token_a and q.token_b == token_b
    ]
    if len(relevant) < 2:
        return 0.0
    lo, hi = min(relevant), max(relevant)
    if lo == 0:
        return 0.0
    return (hi - lo) / lo
