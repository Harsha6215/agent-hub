"""
API Key schemas — request/response models for API key management.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class KeyCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class KeyCreateResponse(BaseModel):
    """Returned only on key creation — full key is shown once."""

    id: UUID
    name: str
    key: str
    key_prefix: str
    created_at: datetime


class KeyResponse(BaseModel):
    id: UUID
    name: str
    key_prefix: str
    is_active: bool
    last_used_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class KeyListResponse(BaseModel):
    keys: list[KeyResponse]
    total: int
