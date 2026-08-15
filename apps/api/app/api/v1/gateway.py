"""
API Gateway — Agent execution endpoint.

Flow: validate → lookup → execute → record → respond
"""

import time

import structlog
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.database import get_db
from apps.api.app.core.exceptions import NotFoundError, ValidationError
from apps.api.app.schemas.gateway import GatewayExecuteRequest, GatewayExecuteResponse
from apps.api.app.services.agent_registry import registry
from apps.api.app.services.usage import record_usage_event

logger = structlog.get_logger(__name__)
router = APIRouter(tags=["Gateway"])


@router.post(
    "/agents/{slug}/execute",
    response_model=GatewayExecuteResponse,
)
async def execute_agent(
    slug: str,
    body: GatewayExecuteRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Execute an agent through the gateway.

    1. Look up agent in registry
    2. Validate input against schema
    3. Execute agent
    4. Record usage event
    5. Return response with latency
    """
    request_id = getattr(request.state, "request_id", "unknown")

    # 1. Lookup agent
    agent = registry.get(slug)
    if not agent:
        raise NotFoundError(f"Agent '{slug}' not found or inactive")

    # 2. Validate input (basic schema check)
    input_schema = agent.get_input_schema()
    required_fields = input_schema.get("required", [])
    for field in required_fields:
        if field not in body.input:
            raise ValidationError(
                f"Missing required field: '{field}'",
                details=[{"field": field, "error": "required"}],
            )

    # 3. Execute
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

    # 4. Record usage (fire-and-forget)
    await record_usage_event(
        db,
        agent_slug=slug,
        status=status,
        latency_ms=int(latency_ms),
        cost_paisa=agent.price_per_request,
        request_meta={"request_id": request_id},
    )

    # 5. Return response
    return GatewayExecuteResponse(
        success=(status == "success"),
        data=result,
        error=error_msg,
        agent=slug,
        version=agent.version,
        latency_ms=latency_ms,
        request_id=request_id,
    )
