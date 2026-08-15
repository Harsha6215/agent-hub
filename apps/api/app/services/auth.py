"""
Auth service — registration, login, token management.
"""

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.exceptions import AuthenticationError, ValidationError
from apps.api.app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from apps.api.app.core.config import settings
from apps.api.app.models.user import User

logger = structlog.get_logger(__name__)


async def register_user(
    db: AsyncSession, *, email: str, password: str, full_name: str | None = None
) -> tuple[User, str, str]:
    """
    Register a new user.

    Returns: (user, access_token, refresh_token)
    Raises: ValidationError if email already exists
    """
    # Check for existing user
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise ValidationError("A user with this email already exists")

    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    logger.info("auth.register", user_id=str(user.id), email=email)
    return user, access_token, refresh_token


async def login_user(
    db: AsyncSession, *, email: str, password: str
) -> tuple[User, str, str]:
    """
    Authenticate user credentials.

    Returns: (user, access_token, refresh_token)
    Raises: AuthenticationError if credentials are invalid
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise AuthenticationError("Invalid email or password")

    if not user.is_active:
        raise AuthenticationError("Account is disabled")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    logger.info("auth.login", user_id=str(user.id))
    return user, access_token, refresh_token


async def refresh_tokens(refresh_token: str) -> tuple[str, str]:
    """
    Verify refresh token and issue new token pair.

    Returns: (new_access_token, new_refresh_token)
    Raises: AuthenticationError if token is invalid
    """
    from jose import JWTError

    try:
        payload = decode_token(refresh_token)
    except JWTError:
        raise AuthenticationError("Invalid or expired refresh token")

    if payload.get("type") != "refresh":
        raise AuthenticationError("Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")

    new_access = create_access_token(user_id)
    new_refresh = create_refresh_token(user_id)

    return new_access, new_refresh
