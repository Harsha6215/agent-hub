"""
UsageEvent model — records every agent execution for metering.
"""

import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.api.app.models.base import BaseModel


class UsageEvent(BaseModel):
    __tablename__ = "usage_events"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    agent_slug: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="success")  # success, error
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    cost_paisa: Mapped[int] = mapped_column(Integer, default=0)
    request_meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    user = relationship("User", back_populates="usage_events")
