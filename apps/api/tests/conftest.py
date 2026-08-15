"""
Test configuration and fixtures.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from apps.api.app.main import app
from apps.api.app.services.agent_registry import registry


@pytest.fixture(autouse=True, scope="session")
def register_agents():
    """Ensure agents are registered for all tests."""
    registry.discover_and_register()


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """
    Async test client for the FastAPI app.

    Each test gets a fresh client. The app is configured with APP_ENV=test
    which disables usage recording to avoid asyncpg conflicts.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
