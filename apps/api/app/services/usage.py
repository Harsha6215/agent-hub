"""
Usage event recording — tracks every agent execution.
"""

import uuid
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


async def record_usage_event(
    db,
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

    This is fire-and-forget — errors are logged but do not propagate
    and do not corrupt the parent session.
    """
    try:
        from apps.api.app.core.database import AsyncSessionLocal
        from apps.api.app.models.usage_event import UsageEvent

        async with AsyncSessionLocal() as session:
            event = UsageEvent(
                user_id=user_id,
                agent_slug=agent_slug,
                status=status,
                latency_ms=latency_ms,
                cost_paisa=cost_paisa,
                request_meta=request_meta,
            )
            session.add(event)
            await session.commit()
        logger.debug("usage.recorded", agent=agent_slug, status=status, latency_ms=latency_ms)
    except Exception as e:
        logger.error("usage.record_failed", error=str(e), agent=agent_slug)
