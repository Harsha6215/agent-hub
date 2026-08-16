"""
Shared Executor — unified execution path for REST and MCP.

Every agent execution (regardless of entry point) flows through here:
  1. Lookup agent in registry
  2. Authenticate (if required)
  3. Rate limit check
  4. Validate input
  5. Execute agent
  6. Record usage (with agent_version + request_id)
  7. Return result
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

import structlog

from apps.api.app.core.config import settings
from apps.api.app.core.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from apps.api.app.services.agent_registry import registry
from apps.api.app.services.rate_limiter import check_rate_limit
from apps.api.app.services.usage import record_usage_event

logger = structlog.get_logger(__name__)


@dataclass
class ExecutionResult:
    """Result of an agent execution."""
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    agent: str = ""
    version: str = ""
    latency_ms: float = 0.0
    request_id: str = ""


async def execute_agent(
    *,
    slug: str,
    input_data: dict[str, Any],
    api_key: str | None = None,
    user_id: uuid.UUID | None = None,
    user_tier: str = "free",
    request_id: str | None = None,
) -> ExecutionResult:
    """
    Unified execution path for both REST and MCP.

    This is the ONLY way agents get executed. No bypassing.
    """
    if not request_id:
        request_id = str(uuid.uuid4())[:8]

    # 1. Lookup agent
    agent = registry.get(slug)
    if not agent:
        raise NotFoundError(f"Agent '{slug}' not found or inactive")

    # 2. Authentication check (production mode)
    if settings.APP_ENV not in ("local", "test"):
        if not api_key and not user_id:
            raise AuthenticationError("API key required. Provide X-API-Key header.")

    # 3. Rate limit (skip in test mode)
    if settings.APP_ENV != "test":
        identity = str(user_id) if user_id else "anonymous"
        allowed, remaining, reset = await check_rate_limit(identity, user_tier)
        if not allowed:
            raise RateLimitError(retry_after=reset)

    # 4. Validate input
    input_schema = agent.get_input_schema()
    required_fields = input_schema.get("required", [])
    for field_name in required_fields:
        if field_name not in input_data:
            raise ValidationError(
                f"Missing required field: '{field_name}'",
                details=[{"field": field_name, "error": "required"}],
            )

    # 5. Execute
    start_time = time.perf_counter()
    status = "success"
    error_msg = None
    result = None
    operation = input_data.get("operation", None)

    try:
        result = await agent.execute(input_data)
    except ValueError as e:
        status = "error"
        error_msg = str(e)
    except Exception as e:
        status = "error"
        error_msg = f"Agent execution failed: {type(e).__name__}"
        logger.error(
            "executor.error",
            slug=slug,
            version=agent.version,
            request_id=request_id,
            error=str(e),
            exc_info=True,
        )

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # 6. Record usage (always — this is the commercial pipeline)
    await record_usage_event(
        db=None,
        user_id=user_id,
        agent_slug=slug,
        status=status,
        latency_ms=int(latency_ms),
        cost_paisa=agent.price_per_request,
        request_meta={
            "request_id": request_id,
            "agent_version": agent.version,
            "operation": operation,
        },
    )

    # 7. Return result
    return ExecutionResult(
        success=(status == "success"),
        data=result,
        error=error_msg,
        agent=slug,
        version=agent.version,
        latency_ms=latency_ms,
        request_id=request_id,
    )
