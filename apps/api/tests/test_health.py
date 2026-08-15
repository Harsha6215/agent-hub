"""
Tests for system health and version endpoints.
"""

import pytest


@pytest.mark.asyncio
async def test_health_root(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "agent-hub"


@pytest.mark.asyncio
async def test_api_health(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_api_version(client):
    response = await client.get("/api/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "env" in data
    assert "name" in data
    assert data["name"] == "Agent Hub"
