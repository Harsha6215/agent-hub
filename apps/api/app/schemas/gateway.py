"""
Gateway schemas — execution request/response models.
"""

from typing import Any

from pydantic import BaseModel, Field


class GatewayExecuteRequest(BaseModel):
    input: dict[str, Any] = Field(..., description="Input data for the agent")


class GatewayExecuteResponse(BaseModel):
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    agent: str
    version: str
    latency_ms: float
    request_id: str | None = None
