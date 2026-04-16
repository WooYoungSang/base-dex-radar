import asyncio
import pytest

from dex_radar.pool_reader import fetch_pool, fetch_all_pools, get_known_pool_infos, _MOCK_PRICES
from dex_radar.models import Pool
from dex_radar.cache import cache_clear


@pytest.fixture(autouse=True)
def clear_cache():
    cache_clear()
    yield
    cache_clear()


def test_known_pool_infos_not_empty():
    pools = get_known_pool_infos()
    assert len(pools) >= 4


def test_known_pool_infos_have_required_fields():
    for p in get_known_pool_infos():
        assert "address" in p
        assert "dex" in p
        assert "token_a" in p
        assert "token_b" in p
        assert "fee" in p


def test_known_pool_dexes():
    dexes = {p["dex"] for p in get_known_pool_infos()}
    assert "uniswap_v3" in dexes
    assert "aerodrome" in dexes


def test_fetch_pool_mock():
    pool_info = {
        "address": "0x4C36388bE6F416A29C8d8Eee81C771cE6bE14B5",
        "dex": "uniswap_v3",
        "token_a": "ETH",
        "token_b": "USDC",
        "fee": 0.0005,
    }
    pool = asyncio.get_event_loop().run_until_complete(fetch_pool(pool_info, None))
    assert isinstance(pool, Pool)
    assert pool.dex == "uniswap_v3"
    assert pool.token_a == "ETH"
    assert pool.price > 0
    assert pool.liquidity > 0
    assert pool.fee == 0.0005


def test_fetch_pool_returns_mock_price():
    addr = "0x4C36388bE6F416A29C8d8Eee81C771cE6bE14B5"
    pool_info = {
        "address": addr,
        "dex": "uniswap_v3",
        "token_a": "ETH",
        "token_b": "USDC",
        "fee": 0.0005,
    }
    pool = asyncio.get_event_loop().run_until_complete(fetch_pool(pool_info, None))
    assert pool.price == _MOCK_PRICES[addr]


def test_fetch_all_pools_no_rpc():
    pools = asyncio.get_event_loop().run_until_complete(fetch_all_pools(use_rpc=False))
    assert len(pools) == len(get_known_pool_infos())
    for p in pools:
        assert isinstance(p, Pool)
        assert p.price > 0


def test_fetch_pool_caches_result():
    pool_info = get_known_pool_infos()[0]
    p1 = asyncio.get_event_loop().run_until_complete(fetch_pool(pool_info, None))
    p2 = asyncio.get_event_loop().run_until_complete(fetch_pool(pool_info, None))
    assert p1 is p2  # same object from cache


def test_all_pools_have_positive_price():
    pools = asyncio.get_event_loop().run_until_complete(fetch_all_pools(use_rpc=False))
    for p in pools:
        assert p.price > 0, f"Pool {p.address} has non-positive price"


def test_all_pools_fees_are_small():
    pools = asyncio.get_event_loop().run_until_complete(fetch_all_pools(use_rpc=False))
    for p in pools:
        assert 0 < p.fee <= 0.01, f"Unexpected fee {p.fee} for pool {p.address}"
