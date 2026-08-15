"""
Tests for Agent CRUD and Gateway endpoints.
"""

import pytest


@pytest.mark.asyncio
async def test_agent_docs_endpoint(client):
    """GET /api/v1/agents/hello/docs returns agent documentation."""
    response = await client.get("/api/v1/agents/hello/docs")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "hello"
    assert data["name"] == "Hello World"
    assert "input_schema" in data
    assert "output_schema" in data


@pytest.mark.asyncio
async def test_agent_docs_not_found(client):
    """GET /api/v1/agents/nonexistent/docs returns 404."""
    response = await client.get("/api/v1/agents/nonexistent/docs")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_gateway_execute_hello(client):
    """POST /api/v1/agents/hello/execute succeeds with valid input."""
    response = await client.post(
        "/api/v1/agents/hello/execute",
        json={"input": {"name": "Test", "language": "en"}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Hello, Test" in data["data"]["greeting"]
    assert data["agent"] == "hello"
    assert data["version"] == "1.0.0"
    assert "latency_ms" in data
    assert "request_id" in data


@pytest.mark.asyncio
async def test_gateway_execute_missing_required_field(client):
    """POST /api/v1/agents/hello/execute fails without required 'name'."""
    response = await client.post(
        "/api/v1/agents/hello/execute",
        json={"input": {"language": "en"}},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert "name" in data["error"]["message"]


@pytest.mark.asyncio
async def test_gateway_execute_agent_not_found(client):
    """POST /api/v1/agents/nonexistent/execute returns 404."""
    response = await client.post(
        "/api/v1/agents/nonexistent/execute",
        json={"input": {"name": "Test"}},
    )
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False


@pytest.mark.asyncio
async def test_gateway_execute_hindi(client):
    """Gateway returns Hindi greeting."""
    response = await client.post(
        "/api/v1/agents/hello/execute",
        json={"input": {"name": "Harsh", "language": "hi"}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Harsh" in data["data"]["greeting"]
