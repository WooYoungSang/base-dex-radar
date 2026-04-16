from dex_radar.models import Pool
from dex_radar.opportunity_detector import find_opportunities


def make_pool(address, dex, token_a, token_b, price, fee=0.003):
    return Pool(address=address, dex=dex, token_a=token_a, token_b=token_b,
                price=price, liquidity=1_000_000, fee=fee)


def test_find_opportunities_detects_spread():
    pools = [
        make_pool("0xAAA", "uniswap_v3", "ETH", "USDC", 3450.0),
        make_pool("0xBBB", "aerodrome", "ETH", "USDC", 3480.0),  # ~0.87% spread
    ]
    opps = find_opportunities(pools)
    assert len(opps) == 1
    opp = opps[0]
    assert opp.buy_dex == "uniswap_v3"
    assert opp.sell_dex == "aerodrome"
    assert opp.buy_price == 3450.0
    assert opp.sell_price == 3480.0


def test_find_opportunities_filters_small_spread():
    pools = [
        make_pool("0xAAA", "uniswap_v3", "ETH", "USDC", 3450.0),
        make_pool("0xBBB", "aerodrome", "ETH", "USDC", 3450.5),  # tiny spread
    ]
    opps = find_opportunities(pools)
    assert len(opps) == 0


def test_find_opportunities_subtracts_fees():
    # Spread ~0.3%, but both pools have 0.2% fee → net negative
    pools = [
        make_pool("0xAAA", "uniswap_v3", "ETH", "USDC", 3450.0, fee=0.002),
        make_pool("0xBBB", "aerodrome", "ETH", "USDC", 3460.0, fee=0.002),
    ]
    opps = find_opportunities(pools)
    # spread = 10/3450 ≈ 0.29%, fees = 0.4% → net negative
    assert len(opps) == 0


def test_find_opportunities_sorted_by_profit():
    pools = [
        make_pool("0xAAA", "uniswap_v3", "ETH", "USDC", 3450.0),
        make_pool("0xBBB", "aerodrome", "ETH", "USDC", 3500.0),
        make_pool("0xCCC", "baseswap", "USDC", "USDT", 1.0),
        make_pool("0xDDD", "sushiswap", "USDC", "USDT", 1.015),
    ]
    opps = find_opportunities(pools)
    assert len(opps) >= 1
    for i in range(len(opps) - 1):
        assert opps[i].estimated_profit_pct >= opps[i + 1].estimated_profit_pct


def test_find_opportunities_empty_pools():
    opps = find_opportunities([])
    assert opps == []


def test_find_opportunities_single_pool():
    pools = [make_pool("0xAAA", "uniswap_v3", "ETH", "USDC", 3450.0)]
    opps = find_opportunities(pools)
    assert opps == []


def test_opportunity_spread_pct_positive():
    pools = [
        make_pool("0xAAA", "uniswap_v3", "ETH", "USDC", 3400.0),
        make_pool("0xBBB", "aerodrome", "ETH", "USDC", 3500.0),
    ]
    opps = find_opportunities(pools)
    assert len(opps) == 1
    assert opps[0].spread_pct > 0
    assert opps[0].estimated_profit_pct > 0
    assert opps[0].estimated_profit_pct < opps[0].spread_pct
