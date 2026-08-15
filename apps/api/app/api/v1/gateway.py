"""
API Gateway — REST entry point for agent execution.

Delegates to the shared executor which handles:
  auth → rate limit → execute → usage → response
"""

import structlog
from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.database import get_db
from apps.api.app.core.security import hash_api_key
from apps.api.app.models.api_key import ApiKey
from apps.api.app.models.user import User
from apps.api.app.schemas.gateway import GatewayExecuteRequest, GatewayExecuteResponse
from apps.api.app.services.executor import execute_agent

logger = structlog.get_logger(__name__)
router = APIRouter(tags=["Gateway"])


async def _resolve_user(x_api_key: str | None, db: AsyncSession) -> tuple:
    """Resolve user from API key. Returns (user_id, tier)."""
    if not x_api_key:
        return None, "free"

    key_hash = hash_api_key(x_api_key)
    result = await db.execute(
        select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.is_active == True)
    )
    api_key = result.scalar_one_or_none()
    if not api_key:
        from apps.api.app.core.exceptions import AuthenticationError
        raise AuthenticationError("Invalid API key")

    result = await db.execute(select(User).where(User.id == api_key.user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        from apps.api.app.core.exceptions import AuthenticationError
        raise AuthenticationError("API key owner not found or inactive")

    # Update last_used
    from datetime import datetime, timezone
    api_key.last_used_at = datetime.now(timezone.utc)

    return user.id, user.tier


@router.post(
    "/agents/{slug}/execute",
    response_model=GatewayExecuteResponse,
)
async def gateway_execute(
    slug: str,
    body: GatewayExecuteRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_api_key: str | None = Header(None, alias="X-API-Key"),
):
    """
    Execute an agent through the REST gateway.

    Uses the shared executor (same path as MCP).
    """
    request_id = (
        getattr(request.state, "request_id", None)
        or request.scope.get("state", {}).get("request_id", "unknown")
    )

    # Resolve user from API key
    user_id, tier = await _resolve_user(x_api_key, db)

    # Delegate to shared executor
    result = await execute_agent(
        slug=slug,
        input_data=body.input,
        api_key=x_api_key,
        user_id=user_id,
        user_tier=tier,
        request_id=request_id,
    )

    return GatewayExecuteResponse(
        success=result.success,
        data=result.data,
        error=result.error,
        agent=result.agent,
        version=result.version,
        latency_ms=result.latency_ms,
        request_id=result.request_id,
    )
