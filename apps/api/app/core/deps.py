"""
Auth dependencies — reusable FastAPI dependencies for authentication and authorization.
"""

from fastapi import Depends, Header
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.database import get_db
from apps.api.app.core.exceptions import AuthenticationError, AuthorizationError
from apps.api.app.core.security import decode_token, hash_api_key
from apps.api.app.models.api_key import ApiKey
from apps.api.app.models.user import User


async def get_current_user(
    authorization: str = Header(..., alias="Authorization"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extract Bearer token from the Authorization header, decode the JWT,
    and load the corresponding user from the database.
    """
    if not authorization.startswith("Bearer "):
        raise AuthenticationError("Invalid authorization header format")

    token = authorization.removeprefix("Bearer ")

    try:
        payload = decode_token(token)
    except JWTError:
        raise AuthenticationError("Invalid or expired token")

    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise AuthenticationError("User not found")

    if not user.is_active:
        raise AuthenticationError("User account is inactive")

    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verify the current user has admin privileges."""
    if not current_user.is_admin:
        raise AuthorizationError("Admin access required")
    return current_user


async def validate_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Read the X-API-Key header, hash it, look up the key in the api_keys table,
    and return the associated user.
    """
    key_hash = hash_api_key(x_api_key)

    result = await db.execute(
        select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.is_active == True)
    )
    api_key = result.scalar_one_or_none()

    if api_key is None:
        raise AuthenticationError("Invalid API key")

    # Load the associated user
    result = await db.execute(select(User).where(User.id == api_key.user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise AuthenticationError("API key owner not found or inactive")

    # Update last_used_at timestamp
    from datetime import datetime, timezone

    api_key.last_used_at = datetime.now(timezone.utc)

    return user
