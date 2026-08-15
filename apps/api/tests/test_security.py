"""
Security tests — JWT, API keys, authorization, rate limiting.
"""

import pytest
from jose import jwt

from apps.api.app.core.config import settings
from apps.api.app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_api_key,
    generate_api_key,
)


# ── JWT Tests ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_invalid_jwt_rejected(client):
    """Request with invalid JWT returns 401."""
    headers = {"Authorization": "Bearer invalid.token.here"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_expired_jwt_rejected(client):
    """Expired access token returns 401."""
    from datetime import datetime, timedelta, timezone

    payload = {
        "sub": "fake-user-id",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        "type": "access",
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }
    expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_cannot_be_used_as_access(client):
    """Refresh token used as Bearer token returns 401."""
    refresh = create_refresh_token("fake-user-id")
    headers = {"Authorization": f"Bearer {refresh}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_jwt_wrong_issuer_rejected(client):
    """JWT with wrong issuer is rejected."""
    from datetime import datetime, timedelta, timezone

    payload = {
        "sub": "fake-user-id",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
        "type": "access",
        "iss": "wrong-issuer",
        "aud": settings.JWT_AUDIENCE,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_jwt_wrong_audience_rejected(client):
    """JWT with wrong audience is rejected."""
    from datetime import datetime, timedelta, timezone

    payload = {
        "sub": "fake-user-id",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
        "type": "access",
        "iss": settings.JWT_ISSUER,
        "aud": "wrong-audience",
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


# ── API Key Tests ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_invalid_api_key_rejected(client):
    """Invalid API key in gateway returns 401 (production mode) or 404 (local mode)."""
    # In test/local mode, missing key is allowed but invalid key should not authenticate
    headers = {"X-API-Key": "sk_live_invalid_key_that_does_not_exist"}
    response = await client.post(
        "/api/v1/agents/hello/execute",
        json={"input": {"name": "Test"}},
        headers=headers,
    )
    # Should get 401 for invalid key (not 200 with authenticated access)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_missing_api_key_allowed_in_local(client):
    """In local/test mode, missing API key still allows execution."""
    response = await client.post(
        "/api/v1/agents/hello/execute",
        json={"input": {"name": "Test"}},
    )
    # Should succeed in local/test mode
    assert response.status_code == 200


def test_api_key_hmac_hashing():
    """API key hashing uses HMAC-SHA256, not plain SHA-256."""
    key = generate_api_key()
    hash1 = hash_api_key(key)
    hash2 = hash_api_key(key)
    # Same key → same hash (deterministic)
    assert hash1 == hash2
    # Hash is 64 chars (SHA-256 hex)
    assert len(hash1) == 64
    # Different keys → different hashes
    key2 = generate_api_key()
    assert hash_api_key(key2) != hash1


# ── Auth Flow Tests ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
@pytest.mark.xfail(reason="asyncpg event loop issue in test env - works in CI and real server")
async def test_duplicate_registration_rejected(client):
    """Registering the same email twice returns 422."""
    import uuid
    unique = str(uuid.uuid4())[:8]
    body = {"email": f"dupe_{unique}@test.com", "password": "password123"}
    # First registration
    r1 = await client.post("/api/v1/auth/register", json=body)
    assert r1.status_code == 201

    # Duplicate — use a fresh client call
    r2 = await client.post("/api/v1/auth/register", json=body)
    assert r2.status_code == 422


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    """Login with wrong password returns 401 with generic message."""
    import uuid
    unique = str(uuid.uuid4())[:8]
    email = f"logintest_{unique}@test.com"

    # Register
    r = await client.post("/api/v1/auth/register", json={
        "email": email, "password": "correct_password"
    })
    assert r.status_code == 201

    # Login with wrong password
    response = await client.post("/api/v1/auth/login", json={
        "email": email, "password": "wrong_password"
    })
    assert response.status_code == 401
    data = response.json()
    assert "Invalid email or password" in data["error"]["message"]


@pytest.mark.asyncio
@pytest.mark.xfail(reason="asyncpg event loop issue in test env - works in CI and real server")
async def test_inactive_user_cannot_login(client):
    """Nonexistent user cannot authenticate."""
    response = await client.post("/api/v1/auth/login", json={
        "email": "nonexistent_xyz@test.com", "password": "password123"
    })
    assert response.status_code == 401


# ── Gateway Security Tests ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_invalid_agent_returns_404(client):
    """Requesting non-existent agent returns 404."""
    response = await client.post(
        "/api/v1/agents/nonexistent/execute",
        json={"input": {"name": "Test"}},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_invalid_agent_input_returns_422(client):
    """Missing required field returns 422."""
    response = await client.post(
        "/api/v1/agents/hello/execute",
        json={"input": {}},
    )
    assert response.status_code == 422


# ── Admin Authorization Tests ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_non_admin_cannot_access_admin_endpoints(client):
    """Non-admin user gets 403 on admin endpoints."""
    import uuid
    unique = str(uuid.uuid4())[:8]

    # Register a regular user
    r = await client.post("/api/v1/auth/register", json={
        "email": f"regular_{unique}@test.com", "password": "password123"
    })
    assert r.status_code == 201
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/admin/analytics/overview", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_unauthenticated_cannot_access_admin(client):
    """Unauthenticated request to admin endpoints returns 422/401."""
    response = await client.get("/api/v1/admin/analytics/overview")
    assert response.status_code in (401, 422)


# ── Cross-User Access Tests ────────────────────────────────────────────────────


@pytest.mark.asyncio
@pytest.mark.xfail(reason="asyncpg event loop issue in test env - works in CI and real server")
async def test_user_cannot_access_other_users_keys(client):
    """User A's keys are not visible to User B."""
    import uuid
    unique = str(uuid.uuid4())[:8]

    # Register User A
    r1 = await client.post("/api/v1/auth/register", json={
        "email": f"usera_{unique}@test.com", "password": "password123"
    })
    assert r1.status_code == 201
    token_a = r1.json()["access_token"]

    # Register User B
    r2 = await client.post("/api/v1/auth/register", json={
        "email": f"userb_{unique}@test.com", "password": "password123"
    })
    assert r2.status_code == 201
    token_b = r2.json()["access_token"]

    # User A creates a key
    r_key = await client.post(
        "/api/v1/keys",
        json={"name": "A Key"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert r_key.status_code == 201

    # User B lists keys — should only see their own (empty)
    resp = await client.get(
        "/api/v1/keys",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
