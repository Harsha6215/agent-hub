"""
Security utilities — password hashing, JWT tokens, and API key management.
"""

import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from apps.api.app.core.config import settings

# ── Password hashing ──────────────────────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT tokens ─────────────────────────────────────────────────────────────────


def create_access_token(subject: str, extra_claims: dict | None = None) -> str:
    """Create a short-lived access token with issuer and audience."""
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": subject,
        "exp": expires,
        "iat": datetime.now(timezone.utc),
        "type": "access",
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """Create a long-lived refresh token with JTI for revocation tracking."""
    expires = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    jti = str(uuid.uuid4())
    payload = {
        "sub": subject,
        "exp": expires,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
        "jti": jti,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT token.

    Validates signature, expiry, issuer, and audience.
    Raises JWTError if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )
        return payload
    except JWTError:
        raise


# ── API key generation ─────────────────────────────────────────────────────────


def generate_api_key(environment: str = "live") -> str:
    """
    Generate a new API key.

    Format: sk_live_<32 random chars> or sk_test_<32 random chars>
    """
    prefix = "sk_live_" if environment == "live" else "sk_test_"
    random_part = secrets.token_urlsafe(32)[:32]
    return f"{prefix}{random_part}"


def hash_api_key(key: str) -> str:
    """
    Hash an API key using HMAC-SHA256 with SECRET_KEY.

    This prevents rainbow table attacks if the database is compromised,
    since the attacker also needs the server's SECRET_KEY.
    """
    return hmac.HMAC(
        settings.SECRET_KEY.encode(), key.encode(), hashlib.sha256
    ).hexdigest()
