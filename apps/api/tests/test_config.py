"""
Tests for application configuration.
"""

import pytest
from apps.api.app.core.config import Settings, get_settings


def test_settings_defaults():
    """Settings load with safe defaults."""
    s = Settings()
    assert s.APP_NAME == "Agent Hub"
    assert s.APP_ENV in ("local", "test")  # Either is fine
    assert s.BACKEND_PORT == 8000
    assert s.DB_POOL_SIZE == 5


def test_settings_singleton():
    """get_settings returns cached instance."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_settings_database_url():
    """DATABASE_URL has asyncpg driver."""
    s = Settings()
    assert "asyncpg" in s.DATABASE_URL


def test_settings_cors_origins():
    """CORS origins include localhost:3000."""
    s = Settings()
    assert "http://localhost:3000" in s.cors_origins_list
