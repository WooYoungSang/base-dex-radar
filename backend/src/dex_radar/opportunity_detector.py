from .models import Pool, Opportunity
from .price_engine import build_price_quotes

MIN_SPREAD_PCT = 0.001  # 0.1% minimum


def find_opportunities(pools: list[Pool]) -> list[Opportunity]:
    quotes = build_price_quotes(pools)
    pairs: set[tuple[str, str]] = set()
    for q in quotes:
        pairs.add((q.token_a, q.token_b))

    opportunities = []
    for token_a, token_b in pairs:
        relevant = [q for q in quotes if q.token_a == token_a and q.token_b == token_b]
        if len(relevant) < 2:
            continue

        relevant.sort(key=lambda q: q.price)
        buy = relevant[0]
        sell = relevant[-1]

        if buy.price == 0:
            continue
        spread = (sell.price - buy.price) / buy.price
        if spread < MIN_SPREAD_PCT:
            continue

        # Subtract fees from both sides
        net_profit = spread - buy.fee - sell.fee
        if net_profit <= 0:
            continue

        opportunities.append(
            Opportunity(
                token_a=token_a,
                token_b=token_b,
                buy_dex=buy.dex,
                sell_dex=sell.dex,
                buy_price=buy.price,
                sell_price=sell.price,
                spread_pct=round(spread * 100, 4),
                estimated_profit_pct=round(net_profit * 100, 4),
                buy_pool=buy.pool_address,
                sell_pool=sell.pool_address,
            )
        )

    opportunities.sort(key=lambda o: o.estimated_profit_pct, reverse=True)
    return opportunities
