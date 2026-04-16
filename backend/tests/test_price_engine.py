import pytest
from dex_radar.models import Pool, PriceQuote
from dex_radar.price_engine import (
    build_price_quotes,
    compare_prices,
    best_buy_quote,
    best_sell_quote,
    price_spread,
)


def make_pool(address, dex, token_a, token_b, price, liquidity=1_000_000, fee=0.003):
    return Pool(address=address, dex=dex, token_a=token_a, token_b=token_b,
                price=price, liquidity=liquidity, fee=fee)


@pytest.fixture
def sample_pools():
    return [
        make_pool("0xAAA", "uniswap_v3", "ETH", "USDC", 3450.0),
        make_pool("0xBBB", "aerodrome", "ETH", "USDC", 3455.0),
        make_pool("0xCCC", "baseswap", "ETH", "USDC", 3448.0),
        make_pool("0xDDD", "sushiswap", "USDC", "USDT", 1.0002),
    ]


def test_build_price_quotes_count(sample_pools):
    quotes = build_price_quotes(sample_pools)
    assert len(quotes) == len(sample_pools)


def test_build_price_quotes_types(sample_pools):
    quotes = build_price_quotes(sample_pools)
    for q in quotes:
        assert isinstance(q, PriceQuote)


def test_compare_prices_filters_correctly(sample_pools):
    quotes = build_price_quotes(sample_pools)
    eth_usdc = compare_prices(quotes, "ETH", "USDC")
    assert len(eth_usdc) == 3
    for q in eth_usdc:
        assert (q.token_a == "ETH" and q.token_b == "USDC") or \
               (q.token_a == "USDC" and q.token_b == "ETH")


def test_best_buy_quote_returns_lowest(sample_pools):
    quotes = build_price_quotes(sample_pools)
    buy = best_buy_quote(quotes, "ETH", "USDC")
    assert buy is not None
    assert buy.price == 3448.0  # baseswap has lowest


def test_best_sell_quote_returns_highest(sample_pools):
    quotes = build_price_quotes(sample_pools)
    sell = best_sell_quote(quotes, "ETH", "USDC")
    assert sell is not None
    assert sell.price == 3455.0  # aerodrome has highest


def test_price_spread_positive(sample_pools):
    quotes = build_price_quotes(sample_pools)
    spread = price_spread(quotes, "ETH", "USDC")
    assert spread > 0


def test_price_spread_value(sample_pools):
    quotes = build_price_quotes(sample_pools)
    spread = price_spread(quotes, "ETH", "USDC")
    expected = (3455.0 - 3448.0) / 3448.0
    assert abs(spread - expected) < 1e-9


def test_price_spread_single_pool():
    pools = [make_pool("0xAAA", "uniswap_v3", "ETH", "USDC", 3450.0)]
    quotes = build_price_quotes(pools)
    assert price_spread(quotes, "ETH", "USDC") == 0.0


def test_no_quotes_for_missing_pair(sample_pools):
    quotes = build_price_quotes(sample_pools)
    result = compare_prices(quotes, "BTC", "ETH")
    assert result == []
