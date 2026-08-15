"""
Agent schemas — request/response models for the agent API.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    slug: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    name: str = Field(..., min_length=2, max_length=255)
    description: str | None = None
    version: str = Field(default="1.0.0", max_length=20)
    category: str = Field(default="utility", max_length=100)
    is_active: bool = True
    is_public: bool = True
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    price_per_request: int = Field(default=0, ge=0)


class AgentUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = None
    version: str | None = Field(None, max_length=20)
    category: str | None = Field(None, max_length=100)
    is_active: bool | None = None
    is_public: bool | None = None
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    price_per_request: int | None = Field(None, ge=0)


class AgentResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    description: str | None
    version: str
    category: str
    is_active: bool
    is_public: bool
    input_schema: dict[str, Any] | None
    output_schema: dict[str, Any] | None
    price_per_request: int
    total_executions: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentListResponse(BaseModel):
    agents: list[AgentResponse]
    total: int
