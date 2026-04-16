"""
Pure-Python BFS multi-hop swap path finder.
KAIROS pathfinder is a compiled binary (not a separable Go module),
so we implement BFS over the known pool graph here.
"""
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Optional

from .models import Pool, SwapRoute

MAX_HOPS = 3
GAS_PER_HOP = 80_000


@dataclass
class _Edge:
    pool: Pool
    from_token: str
    to_token: str

    def price_out(self, amount_in: float) -> float:
        if self.from_token == self.pool.token_a:
            raw = amount_in * self.pool.price
        else:
            raw = amount_in / self.pool.price if self.pool.price else 0.0
        return raw * (1.0 - self.pool.fee)


def _build_graph(pools: list[Pool]) -> dict[str, list[_Edge]]:
    graph: dict[str, list[_Edge]] = defaultdict(list)
    for pool in pools:
        graph[pool.token_a].append(_Edge(pool, pool.token_a, pool.token_b))
        graph[pool.token_b].append(_Edge(pool, pool.token_b, pool.token_a))
    return graph


def find_best_route(
    pools: list[Pool],
    token_in: str,
    token_out: str,
    amount_in: float,
) -> Optional[SwapRoute]:
    if token_in == token_out:
        return None

    graph = _build_graph(pools)

    # BFS state: (current_token, amount_out_so_far, path_tokens, path_pools, path_dexes)
    best: Optional[SwapRoute] = None
    queue: deque = deque()
    queue.append((token_in, amount_in, [token_in], [], []))

    visited_states: set[tuple] = set()

    while queue:
        cur_token, cur_amount, path_tokens, path_pools, path_dexes = queue.popleft()

        if len(path_pools) > MAX_HOPS:
            continue

        state_key = (cur_token, len(path_pools))
        if state_key in visited_states:
            continue
        visited_states.add(state_key)

        for edge in graph.get(cur_token, []):
            if edge.pool.address in path_pools:
                continue

            next_amount = edge.price_out(cur_amount)
            if next_amount <= 0:
                continue

            new_tokens = path_tokens + [edge.to_token]
            new_pools = path_pools + [edge.pool.address]
            new_dexes = path_dexes + [edge.pool.dex]

            if edge.to_token == token_out:
                hops = len(new_pools)
                gas = hops * GAS_PER_HOP
                effective_price = next_amount / amount_in if amount_in else 0.0
                price_impact = _estimate_price_impact(edge.pool, cur_amount)

                route = SwapRoute(
                    token_in=token_in,
                    token_out=token_out,
                    amount_in=amount_in,
                    amount_out=next_amount,
                    path=new_tokens,
                    pools=new_pools,
                    dexes=new_dexes,
                    gas_estimate=gas,
                    price_impact=price_impact,
                    effective_price=effective_price,
                )
                if best is None or next_amount > best.amount_out:
                    best = route
            else:
                if len(new_pools) < MAX_HOPS:
                    queue.append((edge.to_token, next_amount, new_tokens, new_pools, new_dexes))

    return best


def find_all_routes(
    pools: list[Pool],
    token_in: str,
    token_out: str,
    amount_in: float,
) -> list[SwapRoute]:
    if token_in == token_out:
        return []

    graph = _build_graph(pools)
    results: list[SwapRoute] = []
    queue: deque = deque()
    queue.append((token_in, amount_in, [token_in], [], []))

    while queue:
        cur_token, cur_amount, path_tokens, path_pools, path_dexes = queue.popleft()

        if len(path_pools) >= MAX_HOPS:
            continue

        for edge in graph.get(cur_token, []):
            if edge.pool.address in path_pools:
                continue

            next_amount = edge.price_out(cur_amount)
            if next_amount <= 0:
                continue

            new_tokens = path_tokens + [edge.to_token]
            new_pools = path_pools + [edge.pool.address]
            new_dexes = path_dexes + [edge.pool.dex]

            if edge.to_token == token_out:
                hops = len(new_pools)
                results.append(
                    SwapRoute(
                        token_in=token_in,
                        token_out=token_out,
                        amount_in=amount_in,
                        amount_out=next_amount,
                        path=new_tokens,
                        pools=new_pools,
                        dexes=new_dexes,
                        gas_estimate=hops * GAS_PER_HOP,
                        price_impact=_estimate_price_impact(edge.pool, cur_amount),
                        effective_price=next_amount / amount_in if amount_in else 0.0,
                    )
                )
            else:
                queue.append((edge.to_token, next_amount, new_tokens, new_pools, new_dexes))

    results.sort(key=lambda r: r.amount_out, reverse=True)
    return results


def _estimate_price_impact(pool: Pool, amount_in: float) -> float:
    if pool.liquidity <= 0:
        return 0.0
    return min(amount_in / pool.liquidity, 1.0)
