"""
API Gateway — Agent execution endpoint.

Flow: authenticate → rate limit → validate → lookup → execute → record → respond
"""

import time

import structlog
from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.database import get_db
from apps.api.app.core.exceptions import NotFoundError, RateLimitError, ValidationError
from apps.api.app.core.security import hash_api_key
from apps.api.app.models.api_key import ApiKey
from apps.api.app.models.user import User
from apps.api.app.schemas.gateway import GatewayExecuteRequest, GatewayExecuteResponse
from apps.api.app.services.agent_registry import registry
from apps.api.app.services.rate_limiter import check_rate_limit
from apps.api.app.services.usage import record_usage_event

logger = structlog.get_logger(__name__)
router = APIRouter(tags=["Gateway"])


async def _get_user_from_api_key(
    x_api_key: str | None, db: AsyncSession
) -> User | None:
    """Try to authenticate via API key. Returns None if no key provided."""
    if not x_api_key:
        return None

    from sqlalchemy import select

    key_hash = hash_api_key(x_api_key)
    result = await db.execute(
        select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.is_active == True)
    )
    api_key = result.scalar_one_or_none()
    if not api_key:
        return None

    result = await db.execute(select(User).where(User.id == api_key.user_id))
    user = result.scalar_one_or_none()

    # Update last_used_at
    if api_key:
        from datetime import datetime, timezone

        api_key.last_used_at = datetime.now(timezone.utc)

    return user


@router.post(
    "/agents/{slug}/execute",
    response_model=GatewayExecuteResponse,
)
async def execute_agent(
    slug: str,
    body: GatewayExecuteRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_api_key: str | None = Header(None, alias="X-API-Key"),
):
    """
    Execute an agent through the gateway.

    Authentication via X-API-Key header is optional for now.
    When provided, usage is tracked per user and rate limits apply.
    """
    request_id = getattr(request.state, "request_id", "unknown")

    # 1. Authenticate (optional for now — will be required in production)
    user = await _get_user_from_api_key(x_api_key, db)
    user_id = str(user.id) if user else "anonymous"
    tier = user.tier if user else "free"

    # 2. Rate limit check
    allowed, remaining, reset = await check_rate_limit(user_id, tier)
    if not allowed:
        raise RateLimitError(retry_after=reset)

    # 3. Lookup agent
    agent = registry.get(slug)
    if not agent:
        raise NotFoundError(f"Agent '{slug}' not found or inactive")

    # 4. Validate input (basic schema check)
    input_schema = agent.get_input_schema()
    required_fields = input_schema.get("required", [])
    for field in required_fields:
        if field not in body.input:
            raise ValidationError(
                f"Missing required field: '{field}'",
                details=[{"field": field, "error": "required"}],
            )

    # 5. Execute
    start_time = time.perf_counter()
    status = "success"
    error_msg = None
    result = None

    try:
        result = await agent.execute(body.input)
    except ValueError as e:
        status = "error"
        error_msg = str(e)
    except Exception as e:
        status = "error"
        error_msg = f"Agent execution failed: {type(e).__name__}"
        logger.error("gateway.execution_error", slug=slug, error=str(e), exc_info=True)

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # 6. Record usage (fire-and-forget)
    await record_usage_event(
        db,
        user_id=user.id if user else None,
        agent_slug=slug,
        status=status,
        latency_ms=int(latency_ms),
        cost_paisa=agent.price_per_request,
        request_meta={"request_id": request_id},
    )

    # 7. Return response with rate limit headers
    response = GatewayExecuteResponse(
        success=(status == "success"),
        data=result,
        error=error_msg,
        agent=slug,
        version=agent.version,
        latency_ms=latency_ms,
        request_id=request_id,
    )

    return response
