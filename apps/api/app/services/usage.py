"""
Usage event recording — tracks every agent execution.
"""

import uuid
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.models.usage_event import UsageEvent

logger = structlog.get_logger(__name__)


async def record_usage_event(
    db: AsyncSession,
    *,
    user_id: uuid.UUID | None = None,
    agent_slug: str,
    status: str = "success",
    latency_ms: int = 0,
    cost_paisa: int = 0,
    request_meta: dict[str, Any] | None = None,
) -> None:
    """
    Record a usage event. Called after every agent execution.

    This is fire-and-forget — errors are logged but do not propagate.
    """
    try:
        event = UsageEvent(
            user_id=user_id,  # None for anonymous requests
            agent_slug=agent_slug,
            status=status,
            latency_ms=latency_ms,
            cost_paisa=cost_paisa,
            request_meta=request_meta,
        )
        db.add(event)
        await db.flush()
        logger.debug("usage.recorded", agent=agent_slug, status=status, latency_ms=latency_ms)
    except Exception as e:
        logger.error("usage.record_failed", error=str(e), agent=agent_slug)
