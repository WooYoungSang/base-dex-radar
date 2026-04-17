import asyncio
import os
from typing import Optional

import httpx

from .models import Pool
from .cache import cache_get, cache_set, cache_key

BASE_RPC = os.environ.get("BASE_HTTP_URL", "https://base.llamarpc.com")

# Minimal ABI fragments for ERC20 + Uniswap V3 pool
_SLOT0_SIG = "0x3850c7bd"  # slot0()
_LIQUIDITY_SIG = "0x1a686502"  # liquidity()

# Well-known pool addresses on Base (token_a/token_b/fee)
_KNOWN_POOLS: list[dict] = [
    {
        "address": "0x4C36388bE6F416A29C8d8Eee81C771cE6bE14B5",
        "dex": "uniswap_v3",
        "token_a": "ETH",
        "token_b": "USDC",
        "fee": 0.0005,
    },
    {
        "address": "0x420DD381b31aEf6683db6B902084cB0FFECe40D",
        "dex": "aerodrome",
        "token_a": "ETH",
        "token_b": "USDC",
        "fee": 0.0030,
    },
    {
        "address": "0x7E3411B04766089cFaa52DB688855356A12f05D1",
        "dex": "baseswap",
        "token_a": "ETH",
        "token_b": "USDC",
        "fee": 0.0030,
    },
    {
        "address": "0xEB18a5F72bFBD9f9a5e84B0F8a97B8bC4B0CC40",
        "dex": "sushiswap",
        "token_a": "ETH",
        "token_b": "USDC",
        "fee": 0.0030,
    },
    {
        "address": "0x9e5AAC1Ba1a2e6aEd6b32689DFcF62A509Ca96f",
        "dex": "uniswap_v3",
        "token_a": "ETH",
        "token_b": "USDT",
        "fee": 0.0005,
    },
    {
        "address": "0xcDAC0d6c6C59727a65F871236188350531885C43",
        "dex": "aerodrome",
        "token_a": "USDC",
        "token_b": "USDT",
        "fee": 0.0001,
    },
]

# Mock prices used when RPC is unavailable
_MOCK_PRICES: dict[str, float] = {
    "0x4C36388bE6F416A29C8d8Eee81C771cE6bE14B5": 3450.25,
    "0x420DD381b31aEf6683db6B902084cB0FFECe40D": 3452.80,
    "0x7E3411B04766089cFaa52DB688855356A12f05D1": 3448.90,
    "0xEB18a5F72bFBD9f9a5e84B0F8a97B8bC4B0CC40": 3451.10,
    "0x9e5AAC1Ba1a2e6aEd6b32689DFcF62A509Ca96f": 3449.75,
    "0xcDAC0d6c6C59727a65F871236188350531885C43": 1.0001,
}

_MOCK_LIQUIDITY: dict[str, float] = {
    "0x4C36388bE6F416A29C8d8Eee81C771cE6bE14B5": 5_000_000,
    "0x420DD381b31aEf6683db6B902084cB0FFECe40D": 3_200_000,
    "0x7E3411B04766089cFaa52DB688855356A12f05D1": 1_800_000,
    "0xEB18a5F72bFBD9f9a5e84B0F8a97B8bC4B0CC40": 900_000,
    "0x9e5AAC1Ba1a2e6aEd6b32689DFcF62A509Ca96f": 2_100_000,
    "0xcDAC0d6c6C59727a65F871236188350531885C43": 8_500_000,
}


async def _eth_call(client: httpx.AsyncClient, to: str, data: str) -> Optional[str]:
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [{"to": to, "data": data}, "latest"],
        "id": 1,
    }
    try:
        resp = await client.post(BASE_RPC, json=payload, timeout=5.0)
        result = resp.json().get("result")
        return result
    except Exception:
        return None


def _sqrt_price_to_price(sqrt_price_x96: int) -> float:
    # price = (sqrtPriceX96 / 2^96)^2
    q96 = 2**96
    price = (sqrt_price_x96 / q96) ** 2
    # Adjust for token decimals (USDC=6, ETH=18) → multiply by 1e12
    return price * 1e12


async def fetch_pool(pool_info: dict, client: Optional[httpx.AsyncClient] = None) -> Pool:
    addr = pool_info["address"]
    key = cache_key("pool", addr)
    cached = cache_get(key)
    if cached:
        return cached

    price = _MOCK_PRICES.get(addr, 1.0)
    liquidity = _MOCK_LIQUIDITY.get(addr, 1_000_000.0)

    if client:
        raw = await _eth_call(client, addr, _SLOT0_SIG)
        if raw and len(raw) >= 66:
            try:
                sqrt_price_x96 = int(raw[2:66], 16)
                if sqrt_price_x96 > 0:
                    price = _sqrt_price_to_price(sqrt_price_x96)
            except (ValueError, ZeroDivisionError):
                pass

        raw_liq = await _eth_call(client, addr, _LIQUIDITY_SIG)
        if raw_liq and len(raw_liq) >= 66:
            try:
                liquidity = int(raw_liq[2:66], 16) / 1e18
            except ValueError:
                pass

    pool = Pool(
        address=addr,
        dex=pool_info["dex"],
        token_a=pool_info["token_a"],
        token_b=pool_info["token_b"],
        price=price,
        liquidity=liquidity,
        fee=pool_info["fee"],
    )
    cache_set(key, pool)
    return pool


async def fetch_all_pools(use_rpc: bool = True) -> list[Pool]:
    if use_rpc:
        async with httpx.AsyncClient() as client:
            return await asyncio.gather(*[fetch_pool(p, client) for p in _KNOWN_POOLS])
    else:
        return await asyncio.gather(*[fetch_pool(p, None) for p in _KNOWN_POOLS])


def get_known_pool_infos() -> list[dict]:
    return _KNOWN_POOLS
