"""
Bellman-Ford layer-by-layer cycle searcher + A→B route finder.
Cycle searcher ported from wavis-kairos internal/pathfinder/bellman_ford.go.

Finds cyclic arbitrage paths (TokenIn → ... → TokenIn) across Base DEX pools
using the same layer-by-layer frontier expansion as the KAIROS CUDA Phase-2 kernel.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from .models import Pool, SwapRoute

# --- Constants (mirrors wavis-kairos algorithm.go) ---
DEFAULT_MAX_HOPS = 4
MIN_HOPS = 2
MAX_ROUTES = 5_000
GAS_PER_HOP = 80_000


# ---------------------------------------------------------------------------
# Arbitrage cycle types
# ---------------------------------------------------------------------------

@dataclass
class CycleHop:
    pool: str
    token_in: str
    token_out: str
    dex: str


@dataclass
class ArbitrageCycle:
    token: str
    hops: list[CycleHop]
    amount_out_per_unit: float   # output for 1.0 unit input (>1 = profitable)
    profit_pct: float            # (amount_out - 1) * 100
    gas_estimate: int


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_adjacency(pools: list[Pool]) -> dict[str, list[tuple[Pool, str, str]]]:
    adj: dict[str, list[tuple[Pool, str, str]]] = defaultdict(list)
    for pool in pools:
        adj[pool.token_a].append((pool, pool.token_b, "a_to_b"))
        adj[pool.token_b].append((pool, pool.token_a, "b_to_a"))
    return adj


def _price_out(pool: Pool, direction: str, amount_in: float) -> float:
    if direction == "a_to_b":
        return amount_in * pool.price * (1.0 - pool.fee)
    return (amount_in / pool.price) * (1.0 - pool.fee) if pool.price > 0 else 0.0


def _dedup_key(hops: list[CycleHop]) -> str:
    """Canonical key by sorted pool addresses — mirrors dedupKey in Go."""
    return "|".join(sorted(h.pool for h in hops))


# ---------------------------------------------------------------------------
# Bellman-Ford cycle searcher (wavis-kairos port)
# ---------------------------------------------------------------------------

def find_arbitrage_cycles(
    pools: list[Pool],
    token: str,
    max_hops: int = DEFAULT_MAX_HOPS,
) -> list[ArbitrageCycle]:
    """
    Layer-by-layer frontier expansion to find all cyclic paths
    starting and ending at `token`. Identical structural approach to the
    KAIROS CUDA Bellman-Ford GPU kernel (Phase 2).

    Constraints (same as wavis-kairos BellmanFordSearcher):
    - Each pool used at most once per path
    - Intermediate token visited at most once (no token loop)
    - Results capped at MAX_ROUTES
    - Minimum 2 hops, maximum max_hops

    Returns cycles sorted by profit_pct descending.
    """
    if not pools or not token:
        return []

    adj = _build_adjacency(pools)
    results: list[ArbitrageCycle] = []
    seen: set[str] = set()

    # Frontier entry: (current_token, amount_so_far, hops, used_pools, visited_tokens)
    frontier: list[tuple[str, float, list[CycleHop], frozenset, frozenset]] = [
        (token, 1.0, [], frozenset(), frozenset([token]))
    ]

    for hop in range(1, max_hops + 1):
        if len(results) >= MAX_ROUTES:
            break

        next_frontier: list[tuple[str, float, list[CycleHop], frozenset, frozenset]] = []

        for cur_token, cur_amount, cur_hops, used_pools, visited_tokens in frontier:
            for pool, next_token, direction in adj.get(cur_token, []):
                if pool.address in used_pools:
                    continue

                next_amount = _price_out(pool, direction, cur_amount)
                if next_amount <= 0:
                    continue

                new_hop = CycleHop(pool=pool.address, token_in=cur_token, token_out=next_token, dex=pool.dex)
                new_hops = cur_hops + [new_hop]

                if next_token == token and hop >= MIN_HOPS:
                    key = _dedup_key(new_hops)
                    if key not in seen:
                        seen.add(key)
                        results.append(ArbitrageCycle(
                            token=token,
                            hops=new_hops,
                            amount_out_per_unit=round(next_amount, 8),
                            profit_pct=round((next_amount - 1.0) * 100.0, 6),
                            gas_estimate=hop * GAS_PER_HOP,
                        ))
                        if len(results) >= MAX_ROUTES:
                            break
                    continue  # Never extend past cycle closure

                if hop >= max_hops:
                    continue

                if next_token in visited_tokens:
                    continue

                next_frontier.append((
                    next_token,
                    next_amount,
                    new_hops,
                    used_pools | {pool.address},
                    visited_tokens | {next_token},
                ))

        frontier = next_frontier
        if not frontier:
            break

    results.sort(key=lambda c: c.profit_pct, reverse=True)
    return results


# ---------------------------------------------------------------------------
# A→B best-route finder (used by /api/route)
# ---------------------------------------------------------------------------

def find_best_route(
    pools: list[Pool],
    token_in: str,
    token_out: str,
    amount_in: float,
) -> Optional[SwapRoute]:
    if token_in == token_out:
        return None

    adj = _build_adjacency(pools)
    best: Optional[SwapRoute] = None

    # (cur_token, cur_amount, path_tokens, path_pools, path_dexes)
    frontier: list[tuple[str, float, list[str], list[str], list[str]]] = [
        (token_in, amount_in, [token_in], [], [])
    ]
    visited_states: set[tuple] = set()

    for _hop in range(DEFAULT_MAX_HOPS):
        next_frontier = []
        for cur_token, cur_amount, path_tokens, path_pools, path_dexes in frontier:
            state = (cur_token, len(path_pools))
            if state in visited_states:
                continue
            visited_states.add(state)

            for pool, next_token, direction in adj.get(cur_token, []):
                if pool.address in path_pools:
                    continue

                next_amount = _price_out(pool, direction, cur_amount)
                if next_amount <= 0:
                    continue

                new_tokens = path_tokens + [next_token]
                new_pools = path_pools + [pool.address]
                new_dexes = path_dexes + [pool.dex]

                if next_token == token_out:
                    hops = len(new_pools)
                    effective_price = next_amount / amount_in if amount_in else 0.0
                    price_impact = min(cur_amount / pool.liquidity, 1.0) if pool.liquidity > 0 else 0.0
                    route = SwapRoute(
                        token_in=token_in,
                        token_out=token_out,
                        amount_in=amount_in,
                        amount_out=next_amount,
                        path=new_tokens,
                        pools=new_pools,
                        dexes=new_dexes,
                        gas_estimate=hops * GAS_PER_HOP,
                        price_impact=price_impact,
                        effective_price=effective_price,
                    )
                    if best is None or next_amount > best.amount_out:
                        best = route
                else:
                    next_frontier.append((next_token, next_amount, new_tokens, new_pools, new_dexes))

        frontier = next_frontier
        if not frontier:
            break

    return best


def find_all_routes(
    pools: list[Pool],
    token_in: str,
    token_out: str,
    amount_in: float,
) -> list[SwapRoute]:
    if token_in == token_out:
        return []

    adj = _build_adjacency(pools)
    results: list[SwapRoute] = []

    frontier: list[tuple[str, float, list[str], list[str], list[str]]] = [
        (token_in, amount_in, [token_in], [], [])
    ]

    for _hop in range(DEFAULT_MAX_HOPS):
        next_frontier = []
        for cur_token, cur_amount, path_tokens, path_pools, path_dexes in frontier:
            for pool, next_token, direction in adj.get(cur_token, []):
                if pool.address in path_pools:
                    continue
                next_amount = _price_out(pool, direction, cur_amount)
                if next_amount <= 0:
                    continue
                new_tokens = path_tokens + [next_token]
                new_pools = path_pools + [pool.address]
                new_dexes = path_dexes + [pool.dex]
                if next_token == token_out:
                    hops = len(new_pools)
                    results.append(SwapRoute(
                        token_in=token_in, token_out=token_out,
                        amount_in=amount_in, amount_out=next_amount,
                        path=new_tokens, pools=new_pools, dexes=new_dexes,
                        gas_estimate=hops * GAS_PER_HOP,
                        price_impact=min(cur_amount / pool.liquidity, 1.0) if pool.liquidity > 0 else 0.0,
                        effective_price=next_amount / amount_in if amount_in else 0.0,
                    ))
                else:
                    next_frontier.append((next_token, next_amount, new_tokens, new_pools, new_dexes))
        frontier = next_frontier
        if not frontier:
            break

    results.sort(key=lambda r: r.amount_out, reverse=True)
    return results
