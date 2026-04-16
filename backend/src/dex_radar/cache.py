from typing import Any, Optional
from cachetools import TTLCache


_pool_cache: TTLCache = TTLCache(maxsize=1024, ttl=10)  # 10s TTL for pool prices


def cache_get(key: str) -> Optional[Any]:
    return _pool_cache.get(key)


def cache_set(key: str, value: Any) -> None:
    _pool_cache[key] = value


def cache_key(*parts: str) -> str:
    return ":".join(parts)


def cache_clear() -> None:
    _pool_cache.clear()
