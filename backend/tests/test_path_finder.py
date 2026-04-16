import pytest
from dex_radar.models import Pool
from dex_radar.path_finder import find_best_route, find_all_routes, _build_graph


def make_pool(address, dex, token_a, token_b, price, liquidity=1_000_000, fee=0.003):
    return Pool(address=address, dex=dex, token_a=token_a, token_b=token_b,
                price=price, liquidity=liquidity, fee=fee)


@pytest.fixture
def basic_pools():
    return [
        make_pool("0xAAA", "uniswap_v3", "ETH", "USDC", 3450.0),
        make_pool("0xBBB", "aerodrome", "ETH", "USDC", 3455.0),
        make_pool("0xCCC", "baseswap", "USDC", "USDT", 1.0001),
    ]


def test_find_best_route_direct(basic_pools):
    route = find_best_route(basic_pools, "ETH", "USDC", 1.0)
    assert route is not None
    assert route.token_in == "ETH"
    assert route.token_out == "USDC"
    assert len(route.pools) == 1


def test_find_best_route_picks_higher_output(basic_pools):
    route = find_best_route(basic_pools, "ETH", "USDC", 1.0)
    assert route is not None
    # aerodrome has higher price (3455), so amount_out should be based on it
    assert route.amount_out > 3450.0 * 0.99  # accounting for fee


def test_find_best_route_multihop(basic_pools):
    route = find_best_route(basic_pools, "ETH", "USDT", 1.0)
    assert route is not None
    assert route.token_out == "USDT"
    assert len(route.pools) == 2
    assert "USDC" in route.path


def test_find_best_route_same_token(basic_pools):
    route = find_best_route(basic_pools, "ETH", "ETH", 1.0)
    assert route is None


def test_find_best_route_no_path():
    pools = [make_pool("0xAAA", "uniswap_v3", "ETH", "USDC", 3450.0)]
    route = find_best_route(pools, "ETH", "BTC", 1.0)
    assert route is None


def test_find_all_routes_returns_list(basic_pools):
    routes = find_all_routes(basic_pools, "ETH", "USDC", 1.0)
    assert isinstance(routes, list)
    assert len(routes) >= 1


def test_find_all_routes_sorted_by_output(basic_pools):
    routes = find_all_routes(basic_pools, "ETH", "USDC", 1.0)
    for i in range(len(routes) - 1):
        assert routes[i].amount_out >= routes[i + 1].amount_out


def test_route_gas_estimate(basic_pools):
    route = find_best_route(basic_pools, "ETH", "USDC", 1.0)
    assert route is not None
    assert route.gas_estimate == 80_000  # 1 hop


def test_multihop_route_gas(basic_pools):
    route = find_best_route(basic_pools, "ETH", "USDT", 1.0)
    assert route is not None
    assert route.gas_estimate == 160_000  # 2 hops


def test_build_graph_bidirectional(basic_pools):
    graph = _build_graph(basic_pools)
    assert "ETH" in graph
    assert "USDC" in graph
    # ETH->USDC and USDC->ETH edges exist
    eth_neighbors = [e.to_token for e in graph["ETH"]]
    assert "USDC" in eth_neighbors
    usdc_neighbors = [e.to_token for e in graph["USDC"]]
    assert "ETH" in usdc_neighbors
