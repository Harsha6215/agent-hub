"""
Redis connection pool and cache utilities.
"""

from typing import Any

import redis.asyncio as aioredis

from apps.api.app.core.config import settings

_redis_pool: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Get or create Redis connection pool."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=10,
        )
    return _redis_pool


async def close_redis_pool() -> None:
    """Close Redis connection pool on shutdown."""
    global _redis_pool
    if _redis_pool:
        await _redis_pool.close()
        _redis_pool = None


async def cache_get(key: str) -> str | None:
    """Get a value from Redis cache."""
    r = await get_redis()
    return await r.get(key)


async def cache_set(key: str, value: Any, expire: int = 300) -> None:
    """Set a value in Redis cache with expiry (default 5 min)."""
    r = await get_redis()
    await r.set(key, str(value), ex=expire)


async def cache_delete(key: str) -> None:
    """Delete a key from Redis cache."""
    r = await get_redis()
    await r.delete(key)
