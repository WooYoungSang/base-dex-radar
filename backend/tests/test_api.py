import pytest
from fastapi.testclient import TestClient

from dex_radar.api import app
from dex_radar.models import Pool
from dex_radar.cache import cache_clear

ADDR1 = "0xAAA0000000000000000000000000000000000001"
ADDR2 = "0xAAA0000000000000000000000000000000000002"
ADDR3 = "0xAAA0000000000000000000000000000000000003"


def make_pool(address, dex, token_a, token_b, price, fee=0.003):
    return Pool(address=address, dex=dex, token_a=token_a, token_b=token_b,
                price=price, liquidity=2_000_000, fee=fee)


TEST_POOLS = [
    make_pool(ADDR1, "uniswap_v3", "ETH", "USDC", 3450.0, fee=0.0005),
    make_pool(ADDR2, "aerodrome", "ETH", "USDC", 3460.0, fee=0.003),
    make_pool(ADDR3, "baseswap", "USDC", "USDT", 1.0001, fee=0.001),
]


async def _mock_fetch_all_pools(use_rpc: bool = True):
    return TEST_POOLS


@pytest.fixture(autouse=True)
def seed_pools(monkeypatch):
    cache_clear()
    import dex_radar.api as api_module
    monkeypatch.setattr(api_module, "fetch_all_pools", _mock_fetch_all_pools)
    yield
    cache_clear()


@pytest.fixture
def client(seed_pools):
    with TestClient(app) as c:
        yield c


# Health
def test_health_ok(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"


def test_health_pools_loaded(client):
    r = client.get("/api/health")
    assert r.json()["pools_loaded"] == 3


# Prices
def test_prices_eth_usdc(client):
    r = client.get("/api/prices?token_a=ETH&token_b=USDC")
    assert r.status_code == 200
    data = r.json()
    assert data["pair"] == "ETH/USDC"
    assert len(data["quotes"]) == 2


def test_prices_case_insensitive(client):
    r = client.get("/api/prices?token_a=eth&token_b=usdc")
    assert r.status_code == 200


def test_prices_not_found(client):
    r = client.get("/api/prices?token_a=BTC&token_b=SOL")
    assert r.status_code == 404


def test_prices_quote_fields(client):
    r = client.get("/api/prices?token_a=ETH&token_b=USDC")
    quote = r.json()["quotes"][0]
    assert "dex" in quote
    assert "price" in quote
    assert "pool_address" in quote
    assert quote["price"] > 0


# Route
def test_route_direct(client):
    r = client.get("/api/route?token_a=ETH&token_b=USDC&amount=1.0")
    assert r.status_code == 200
    data = r.json()
    assert data["token_in"] == "ETH"
    assert data["token_out"] == "USDC"
    assert data["amount_out"] > 0


def test_route_multihop(client):
    r = client.get("/api/route?token_a=ETH&token_b=USDT&amount=1.0")
    assert r.status_code == 200
    data = r.json()
    assert len(data["pools"]) == 2


def test_route_not_found(client):
    r = client.get("/api/route?token_a=ETH&token_b=BTC&amount=1.0")
    assert r.status_code == 404


# Liquidity
def test_liquidity_found(client):
    addr = "0xAAA0000000000000000000000000000000000001"
    r = client.get(f"/api/liquidity/{addr}")
    assert r.status_code == 200
    data = r.json()
    assert data["pool_address"] == addr
    assert len(data["bids"]) > 0
    assert len(data["asks"]) > 0


def test_liquidity_not_found(client):
    r = client.get("/api/liquidity/0xDEAD")
    assert r.status_code == 404


def test_liquidity_case_insensitive(client):
    addr = "0xaaa0000000000000000000000000000000000001"
    r = client.get(f"/api/liquidity/{addr}")
    assert r.status_code == 200


# Gas
def test_gas_response(client):
    r = client.get("/api/gas")
    assert r.status_code == 200
    data = r.json()
    assert "base_fee_gwei" in data
    assert "estimated_swap_usd" in data
    assert data["estimated_swap_usd"] >= 0


# Opportunities
def test_opportunities_returns_list(client):
    r = client.get("/api/opportunities")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_opportunities_fields(client):
    r = client.get("/api/opportunities")
    opps = r.json()
    if opps:
        opp = opps[0]
        assert "buy_dex" in opp
        assert "sell_dex" in opp
        assert "spread_pct" in opp
        assert opp["estimated_profit_pct"] >= 0


# Swagger docs
def test_swagger_docs(client):
    r = client.get("/docs")
    assert r.status_code == 200


def test_openapi_json(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schema = r.json()
    assert "paths" in schema
    assert "/api/prices" in schema["paths"]
