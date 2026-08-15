"""
Base model mixin with common columns.
"""

import uuid

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.app.core.database import Base, TimestampMixin


class BaseModel(Base, TimestampMixin):
    """Abstract base that provides id, created_at, updated_at."""

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
