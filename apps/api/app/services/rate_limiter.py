"""
Rate limiter — Redis sliding window implementation.
"""

import time

import structlog

from apps.api.app.core.cache import get_redis

logger = structlog.get_logger(__name__)

# Rate limits per tier (requests per day)
TIER_LIMITS = {
    "free": 100,
    "developer": 1000,
    "pro": 10000,
    "enterprise": 100000,
}


async def check_rate_limit(
    user_id: str, tier: str = "free"
) -> tuple[bool, int, int]:
    """
    Check if user is within rate limit.

    Returns: (allowed: bool, remaining: int, reset_seconds: int)
    """
    limit = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
    key = f"ratelimit:{user_id}:daily"

    try:
        redis = await get_redis()
        current = await redis.get(key)

        if current is None:
            # First request today — set counter with 24h TTL
            await redis.set(key, 1, ex=86400)
            return True, limit - 1, 86400

        count = int(current)
        if count >= limit:
            ttl = await redis.ttl(key)
            return False, 0, max(ttl, 0)

        await redis.incr(key)
        remaining = limit - count - 1
        ttl = await redis.ttl(key)
        return True, remaining, max(ttl, 0)

    except Exception as e:
        # If Redis is down, allow the request but log the issue
        logger.error("rate_limiter.redis_error", error=str(e))
        return True, limit, 86400
