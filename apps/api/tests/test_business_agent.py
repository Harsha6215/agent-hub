"""
Tests for Business Calculator Agent.
"""

import pytest
from agents.business.agent import BusinessCalculatorAgent


@pytest.fixture
def agent():
    return BusinessCalculatorAgent()


# ── Metadata ───────────────────────────────────────────────────────────────────

def test_agent_metadata(agent):
    assert agent.slug == "business-calculator"
    assert agent.name == "Business Calculator"
    assert agent.version == "1.0.0"
    assert agent.category == "finance"
    assert agent.price_per_request == 10


# ── Profit ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_profit_basic(agent):
    result = await agent.execute({
        "operation": "profit",
        "cost": "600",
        "selling_price": "1000",
    })
    assert result["profit"] == "400.00"
    assert result["margin_percent"] == "40.00"
    assert result["markup_percent"] == "66.67"


@pytest.mark.asyncio
async def test_profit_zero_cost(agent):
    result = await agent.execute({
        "operation": "profit",
        "cost": "0",
        "selling_price": "500",
    })
    assert result["profit"] == "500.00"
    assert result["markup_percent"] == "0.00"  # Can't divide by 0 cost


@pytest.mark.asyncio
async def test_profit_loss(agent):
    """Selling below cost = negative profit."""
    result = await agent.execute({
        "operation": "profit",
        "cost": "1000",
        "selling_price": "750",
    })
    assert result["profit"] == "-250.00"


# ── Margin ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_margin(agent):
    result = await agent.execute({
        "operation": "margin",
        "cost": "750",
        "selling_price": "1000",
    })
    assert result["margin_percent"] == "25.00"
    assert result["profit"] == "250.00"


@pytest.mark.asyncio
async def test_margin_zero_selling_price(agent):
    with pytest.raises(ValueError, match="selling_price must be greater than 0"):
        await agent.execute({
            "operation": "margin",
            "cost": "500",
            "selling_price": "0",
        })


# ── Markup ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_markup(agent):
    result = await agent.execute({
        "operation": "markup",
        "cost": "600",
        "selling_price": "1000",
    })
    assert result["markup_percent"] == "66.67"


@pytest.mark.asyncio
async def test_markup_zero_cost(agent):
    with pytest.raises(ValueError, match="cost must be greater than 0"):
        await agent.execute({
            "operation": "markup",
            "cost": "0",
            "selling_price": "1000",
        })


# ── Break-even ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_breakeven(agent):
    result = await agent.execute({
        "operation": "breakeven",
        "fixed_costs": "10000",
        "price_per_unit": "100",
        "variable_cost_per_unit": "60",
    })
    assert result["breakeven_units"] == "250"
    assert result["contribution_per_unit"] == "40.00"
    assert result["breakeven_revenue"] == "25000.00"


@pytest.mark.asyncio
async def test_breakeven_no_contribution(agent):
    with pytest.raises(ValueError, match="price_per_unit must exceed"):
        await agent.execute({
            "operation": "breakeven",
            "fixed_costs": "10000",
            "price_per_unit": "50",
            "variable_cost_per_unit": "60",
        })


# ── Discount ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_discount(agent):
    result = await agent.execute({
        "operation": "discount",
        "original_price": "1000",
        "discount_percent": "20",
    })
    assert result["savings"] == "200.00"
    assert result["final_price"] == "800.00"


@pytest.mark.asyncio
async def test_discount_invalid_percent(agent):
    with pytest.raises(ValueError, match="discount_percent must be between"):
        await agent.execute({
            "operation": "discount",
            "original_price": "1000",
            "discount_percent": "150",
        })


# ── Invalid operation ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_invalid_operation(agent):
    with pytest.raises(ValueError, match="Unknown operation"):
        await agent.execute({"operation": "nonexistent"})


# ── Integration (via HTTP client) ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rest_gateway_execution(client):
    """Business Calculator works through REST gateway."""
    response = await client.post(
        "/api/v1/agents/business-calculator/execute",
        json={"input": {"operation": "profit", "cost": "600", "selling_price": "1000"}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["profit"] == "400.00"
    assert data["agent"] == "business-calculator"
    assert data["version"] == "1.0.0"
    assert "request_id" in data


@pytest.mark.asyncio
async def test_mcp_tool_discovery(client):
    """Business Calculator appears in MCP tools list."""
    response = await client.get("/mcp/tools")
    assert response.status_code == 200
    tools = response.json()["tools"]
    slugs = [t["name"] for t in tools]
    assert "business-calculator" in slugs


@pytest.mark.asyncio
async def test_mcp_tool_execution(client):
    """Business Calculator works through MCP tools/call."""
    response = await client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "business-calculator",
                "arguments": {
                    "operation": "discount",
                    "original_price": "500",
                    "discount_percent": "10",
                },
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["content"][0]["type"] == "text"
    # Parse the JSON text content
    import json
    result = json.loads(data["result"]["content"][0]["text"])
    assert result["final_price"] == "450.00"
