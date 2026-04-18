"""
GPU Bellman-Ford cycle searcher — Python ctypes bindings for libbellman.so.
Ported interface from wavis-kairos internal/pathfinder/cuda/bellman_ford.cu.

Falls back to CPU (find_arbitrage_cycles) if GPU is unavailable.
"""
from __future__ import annotations

import ctypes
import logging
import os
from typing import Optional

from .models import Pool
from .path_finder import ArbitrageCycle, CycleHop, GAS_PER_HOP

logger = logging.getLogger(__name__)

_lib: Optional[ctypes.CDLL] = None
_cudart: Optional[ctypes.CDLL] = None
_gpu_available: Optional[bool] = None

_SO_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "libbellman.so")
_H2D = 1  # cudaMemcpyHostToDevice


class _GPUGraphBuffers(ctypes.Structure):
    _fields_ = [
        ("d_row_ptr",   ctypes.c_void_p),
        ("d_col_idx",   ctypes.c_void_p),
        ("d_edge_pool", ctypes.c_void_p),
        ("num_tokens",  ctypes.c_int),
        ("num_edges",   ctypes.c_int),
        ("allocated",   ctypes.c_int),
    ]


def _load_libs() -> bool:
    global _lib, _cudart, _gpu_available
    if _gpu_available is not None:
        return _gpu_available
    try:
        _cudart = ctypes.CDLL("libcudart.so")
        _cudart.cudaMalloc.restype  = ctypes.c_int
        _cudart.cudaMalloc.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_size_t]
        _cudart.cudaMemcpy.restype  = ctypes.c_int
        _cudart.cudaFree.restype    = ctypes.c_int

        so = os.path.realpath(_SO_PATH)
        _lib = ctypes.CDLL(so)
        _lib.gpu_bellman_ford_search.restype  = None
        _lib.gpu_bellman_ford_search.argtypes = [
            ctypes.POINTER(_GPUGraphBuffers),
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_int)),
            ctypes.POINTER(ctypes.c_int),
        ]
        _gpu_available = True
        logger.info("GPU Bellman-Ford loaded from %s", so)
    except Exception as e:
        _gpu_available = False
        logger.debug("GPU unavailable (%s), will use CPU path", e)
    return _gpu_available


def _cuda_upload(data: list[int]) -> ctypes.c_void_p:
    arr = (ctypes.c_int * len(data))(*data)
    ptr = ctypes.c_void_p()
    rc = _cudart.cudaMalloc(ctypes.byref(ptr), len(data) * 4)
    if rc != 0:
        raise RuntimeError(f"cudaMalloc failed rc={rc}")
    _cudart.cudaMemcpy(ptr, arr, len(data) * 4, _H2D)
    return ptr


def _cuda_free(*ptrs) -> None:
    for p in ptrs:
        if p:
            _cudart.cudaFree(p)


def _build_csr(pools: list[Pool]):
    """
    Build CSR adjacency for the GPU kernel.
    Returns:
      token_list, row_ptr, col_idx, edge_pool_idx,
      edge_meta: list of (Pool, direction) per directed edge
        direction: 'a_to_b' or 'b_to_a'
    """
    token_idx: dict[str, int] = {}
    token_list: list[str] = []
    pool_idx: dict[str, int] = {}

    for p in pools:
        for t in (p.token_a, p.token_b):
            if t not in token_idx:
                token_idx[t] = len(token_list)
                token_list.append(t)
        if p.address not in pool_idx:
            pool_idx[p.address] = len(pool_idx)

    n = len(token_list)
    adj: list[list[tuple[int, int, Pool, str]]] = [[] for _ in range(n)]
    for p in pools:
        ia = token_idx[p.token_a]
        ib = token_idx[p.token_b]
        pi = pool_idx[p.address]
        adj[ia].append((ib, pi, p, "a_to_b"))
        adj[ib].append((ia, pi, p, "b_to_a"))

    row_ptr: list[int] = [0] * (n + 1)
    col_idx: list[int] = []
    ep: list[int] = []
    edge_meta: list[tuple[Pool, str]] = []  # (pool, direction)

    for t in range(n):
        for dest, pi, pool, direction in adj[t]:
            col_idx.append(dest)
            ep.append(pi)
            edge_meta.append((pool, direction))
        row_ptr[t + 1] = len(col_idx)

    return token_list, token_idx, row_ptr, col_idx, ep, edge_meta


def _profit(hops: list[CycleHop], pools: list[Pool]) -> float:
    """Calculate amount out for 1.0 unit in over the cycle."""
    pool_map = {p.address: p for p in pools}
    amount = 1.0
    for hop in hops:
        p = pool_map.get(hop.pool)
        if p is None or amount <= 0:
            return 0.0
        if hop.token_in == p.token_a:
            amount = amount * p.price * (1.0 - p.fee)
        else:
            amount = (amount / p.price * (1.0 - p.fee)) if p.price > 0 else 0.0
    return amount


def find_arbitrage_cycles_gpu(
    pools: list[Pool],
    token: str,
    max_hops: int = 4,
) -> tuple[list[ArbitrageCycle], bool]:
    """
    GPU Bellman-Ford cycle search.
    Returns (cycles, used_gpu). used_gpu=False → fell back to CPU path.
    """
    if not _load_libs():
        return [], False

    try:
        token_list, token_idx, row_ptr, col_idx, ep, edge_meta = _build_csr(pools)

        if token not in token_idx:
            return [], True

        start = token_idx[token]

        d_row = _cuda_upload(row_ptr)
        d_col = _cuda_upload(col_idx)
        d_ep  = _cuda_upload(ep)

        buf = _GPUGraphBuffers()
        buf.d_row_ptr   = d_row
        buf.d_col_idx   = d_col
        buf.d_edge_pool = d_ep
        buf.num_tokens  = len(token_list)
        buf.num_edges   = len(col_idx)
        buf.allocated   = 1

        out_paths = ctypes.POINTER(ctypes.c_int)()
        out_count = ctypes.c_int(0)

        _lib.gpu_bellman_ford_search(
            ctypes.byref(buf),
            start, max_hops, 5000,
            ctypes.byref(out_paths),
            ctypes.byref(out_count),
        )

        _cuda_free(d_row, d_col, d_ep)

        cycles: list[ArbitrageCycle] = []
        n_results = out_count.value

        for p_idx in range(n_results):
            hops: list[CycleHop] = []
            for h in range(max_hops):
                ei = out_paths[p_idx * max_hops + h]
                if ei < 0:
                    break
                pool_obj, direction = edge_meta[ei]
                tok_in  = pool_obj.token_a if direction == "a_to_b" else pool_obj.token_b
                tok_out = pool_obj.token_b if direction == "a_to_b" else pool_obj.token_a
                hops.append(CycleHop(pool=pool_obj.address, token_in=tok_in, token_out=tok_out, dex=pool_obj.dex))

            if not hops:
                continue

            amount = _profit(hops, pools)
            cycles.append(ArbitrageCycle(
                token=token,
                hops=hops,
                amount_out_per_unit=round(amount, 8),
                profit_pct=round((amount - 1.0) * 100.0, 6),
                gas_estimate=len(hops) * GAS_PER_HOP,
            ))

        if out_paths:
            ctypes.CDLL("libc.so.6").free(out_paths)

        # Dedup by sorted pool set — keep best profit per pool set (mirrors CPU dedupKey)
        best_by_key: dict[str, ArbitrageCycle] = {}
        for c in cycles:
            key = "|".join(sorted(h.pool for h in c.hops))
            if key not in best_by_key or c.profit_pct > best_by_key[key].profit_pct:
                best_by_key[key] = c

        deduped = sorted(best_by_key.values(), key=lambda c: c.profit_pct, reverse=True)
        return deduped, True

    except Exception as e:
        logger.warning("GPU search error (%s), falling back to CPU", e)
        return [], False
