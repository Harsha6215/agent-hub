"""
API Key management service — create, validate, list, revoke keys.
"""

import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.security import generate_api_key, hash_api_key
from apps.api.app.models.api_key import ApiKey
from apps.api.app.models.user import User

logger = structlog.get_logger(__name__)


async def create_key(
    db: AsyncSession, *, user: User, name: str
) -> tuple[ApiKey, str]:
    """
    Generate a new API key for a user.

    Returns: (api_key_record, full_key)
    The full key is only returned once — it's not stored.
    """
    full_key = generate_api_key(environment="live")
    key_hash = hash_api_key(full_key)
    key_prefix = full_key[:12]  # e.g., "sk_live_abc1"

    api_key = ApiKey(
        user_id=user.id,
        name=name,
        key_prefix=key_prefix,
        key_hash=key_hash,
    )
    db.add(api_key)
    await db.flush()
    await db.refresh(api_key)

    logger.info("key.created", user_id=str(user.id), key_prefix=key_prefix)
    return api_key, full_key


async def list_keys(db: AsyncSession, *, user: User) -> list[ApiKey]:
    """List all API keys for a user (prefix only, no full key)."""
    result = await db.execute(
        select(ApiKey)
        .where(ApiKey.user_id == user.id)
        .order_by(ApiKey.created_at.desc())
    )
    return list(result.scalars().all())


async def revoke_key(
    db: AsyncSession, *, user: User, key_id: uuid.UUID
) -> bool:
    """Revoke (deactivate) an API key."""
    result = await db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user.id)
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        return False

    api_key.is_active = False
    await db.flush()
    logger.info("key.revoked", key_prefix=api_key.key_prefix)
    return True
