"""
Rate limiter — atomic Redis INCR-based implementation.

Uses atomic INCR to prevent race conditions where concurrent requests
could bypass limits.
"""

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

_RATE_LIMIT_TTL = 86400  # 24 hours


async def check_rate_limit(
    user_id: str, tier: str = "free"
) -> tuple[bool, int, int]:
    """
    Check if user is within rate limit using atomic INCR.

    The INCR operation is atomic — even under concurrent requests,
    the count will be accurate and limits cannot be bypassed.

    Returns: (allowed: bool, remaining: int, reset_seconds: int)
    """
    limit = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
    key = f"ratelimit:{user_id}:daily"

    try:
        redis = await get_redis()

        # Atomic increment — this is the core fix for the race condition.
        # INCR creates the key with value 1 if it doesn't exist.
        count = await redis.incr(key)

        # Set expiry only on first request (when count becomes 1)
        if count == 1:
            await redis.expire(key, _RATE_LIMIT_TTL)

        ttl = await redis.ttl(key)
        # Safety: if TTL somehow wasn't set, fix it
        if ttl < 0:
            await redis.expire(key, _RATE_LIMIT_TTL)
            ttl = _RATE_LIMIT_TTL

        if count > limit:
            return False, 0, max(ttl, 0)

        remaining = limit - count
        return True, remaining, max(ttl, 0)

    except Exception as e:
        # If Redis is down, allow the request but log the issue.
        # In production, consider failing closed instead.
        logger.error("rate_limiter.redis_error", error=str(e))
        return True, limit, _RATE_LIMIT_TTL
