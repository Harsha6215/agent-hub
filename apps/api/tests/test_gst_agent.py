"""
Tests for GST Calculator Agent.
Covers: unit tests, API tests, MCP tests, validation, precision, regression.
"""

import json

import pytest
from agents.gst.agent import GSTCalculatorAgent


@pytest.fixture
def agent():
    return GSTCalculatorAgent()


# ── Metadata ───────────────────────────────────────────────────────────────────

def test_gst_metadata(agent):
    assert agent.slug == "gst-calculator"
    assert agent.name == "GST Calculator"
    assert agent.version == "1.0.0"
    assert agent.category == "finance"
    assert agent.price_per_request == 10


# ── Forward GST (calculate_gst) ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_calculate_gst_18(agent):
    """18% GST on ₹1000 = ₹180 GST, ₹1180 total."""
    result = await agent.execute({
        "operation": "calculate_gst",
        "amount": "1000",
        "gst_rate": "18",
    })
    assert result["base_amount"] == "1000.00"
    assert result["gst_amount"] == "180.00"
    assert result["total_amount"] == "1180.00"
    assert result["cgst"] == "90.00"
    assert result["sgst"] == "90.00"


@pytest.mark.asyncio
async def test_calculate_gst_5(agent):
    """5% GST."""
    result = await agent.execute({
        "operation": "calculate_gst",
        "amount": "2000",
        "gst_rate": "5",
    })
    assert result["gst_amount"] == "100.00"
    assert result["total_amount"] == "2100.00"


@pytest.mark.asyncio
async def test_calculate_gst_28(agent):
    """28% GST (luxury)."""
    result = await agent.execute({
        "operation": "calculate_gst",
        "amount": "5000",
        "gst_rate": "28",
    })
    assert result["gst_amount"] == "1400.00"
    assert result["total_amount"] == "6400.00"


@pytest.mark.asyncio
async def test_calculate_gst_zero_rate(agent):
    """0% GST = no tax."""
    result = await agent.execute({
        "operation": "calculate_gst",
        "amount": "1000",
        "gst_rate": "0",
    })
    assert result["gst_amount"] == "0.00"
    assert result["total_amount"] == "1000.00"


@pytest.mark.asyncio
async def test_calculate_gst_interstate(agent):
    """Inter-state: IGST instead of CGST/SGST."""
    result = await agent.execute({
        "operation": "calculate_gst",
        "amount": "1000",
        "gst_rate": "18",
        "is_interstate": True,
    })
    assert result["igst"] == "180.00"
    assert "cgst" not in result
    assert "sgst" not in result


@pytest.mark.asyncio
async def test_calculate_gst_intrastate(agent):
    """Intra-state: CGST + SGST split."""
    result = await agent.execute({
        "operation": "calculate_gst",
        "amount": "1000",
        "gst_rate": "12",
        "is_interstate": False,
    })
    assert result["cgst"] == "60.00"
    assert result["sgst"] == "60.00"
    assert "igst" not in result


# ── Reverse GST (extract_gst) ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_extract_gst_18(agent):
    """Extract base from ₹1180 at 18% → ₹1000 base, ₹180 GST."""
    result = await agent.execute({
        "operation": "extract_gst",
        "amount": "1180",
        "gst_rate": "18",
    })
    assert result["base_amount"] == "1000.00"
    assert result["gst_amount"] == "180.00"
    assert result["cgst"] == "90.00"
    assert result["sgst"] == "90.00"


@pytest.mark.asyncio
async def test_extract_gst_5(agent):
    """Reverse at 5%."""
    result = await agent.execute({
        "operation": "extract_gst",
        "amount": "1050",
        "gst_rate": "5",
    })
    assert result["base_amount"] == "1000.00"
    assert result["gst_amount"] == "50.00"


@pytest.mark.asyncio
async def test_extract_gst_interstate(agent):
    """Reverse with IGST."""
    result = await agent.execute({
        "operation": "extract_gst",
        "amount": "1180",
        "gst_rate": "18",
        "is_interstate": True,
    })
    assert result["igst"] == "180.00"


@pytest.mark.asyncio
async def test_extract_gst_rounding_note(agent):
    """Reverse calculation includes rounding documentation."""
    result = await agent.execute({
        "operation": "extract_gst",
        "amount": "999.99",
        "gst_rate": "18",
    })
    assert "rounding_note" in result


# ── Precision Tests ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_precision_odd_amount(agent):
    """Decimal precision on odd amounts."""
    result = await agent.execute({
        "operation": "calculate_gst",
        "amount": "333.33",
        "gst_rate": "18",
    })
    # 333.33 * 0.18 = 59.9994 → rounds to 60.00
    assert result["gst_amount"] == "60.00"
    assert result["total_amount"] == "393.33"


@pytest.mark.asyncio
async def test_precision_small_amount(agent):
    """Very small amount."""
    result = await agent.execute({
        "operation": "calculate_gst",
        "amount": "1.50",
        "gst_rate": "18",
    })
    # 1.50 * 0.18 = 0.27
    assert result["gst_amount"] == "0.27"
    assert result["total_amount"] == "1.77"


# ── Invoice Total ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_invoice_total_basic(agent):
    """Basic invoice with two items."""
    result = await agent.execute({
        "operation": "invoice_total",
        "items": [
            {"name": "Product A", "quantity": 2, "unit_price": "500.00"},
            {"name": "Product B", "quantity": 1, "unit_price": "300.00"},
        ],
        "discount": "50.00",
        "gst_rate": "18",
    })
    # Subtotal: 2*500 + 1*300 = 1300
    # Taxable: 1300 - 50 = 1250
    # GST: 1250 * 0.18 = 225
    # Grand total: 1250 + 225 = 1475
    assert result["subtotal"] == "1300.00"
    assert result["discount"] == "50.00"
    assert result["taxable_value"] == "1250.00"
    assert result["gst_amount"] == "225.00"
    assert result["grand_total"] == "1475.00"
    assert result["cgst"] == "112.50"
    assert result["sgst"] == "112.50"


@pytest.mark.asyncio
async def test_invoice_total_no_discount(agent):
    """Invoice without discount."""
    result = await agent.execute({
        "operation": "invoice_total",
        "items": [
            {"name": "Widget", "quantity": 5, "unit_price": "200"},
        ],
        "gst_rate": "12",
    })
    assert result["subtotal"] == "1000.00"
    assert result["discount"] == "0.00"
    assert result["taxable_value"] == "1000.00"
    assert result["gst_amount"] == "120.00"
    assert result["grand_total"] == "1120.00"


# ── Validation Tests ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_invalid_gst_rate(agent):
    """Invalid rate (e.g., 15%) is rejected."""
    with pytest.raises(ValueError, match="Invalid GST rate"):
        await agent.execute({
            "operation": "calculate_gst",
            "amount": "1000",
            "gst_rate": "15",
        })


@pytest.mark.asyncio
async def test_negative_amount(agent):
    """Negative amount rejected."""
    with pytest.raises(ValueError, match="must be non-negative"):
        await agent.execute({
            "operation": "calculate_gst",
            "amount": "-500",
            "gst_rate": "18",
        })


@pytest.mark.asyncio
async def test_empty_items(agent):
    """Invoice with no items rejected."""
    with pytest.raises(ValueError, match="items array is required"):
        await agent.execute({
            "operation": "invoice_total",
            "items": [],
            "gst_rate": "18",
        })


@pytest.mark.asyncio
async def test_discount_exceeds_subtotal(agent):
    """Discount > subtotal rejected."""
    with pytest.raises(ValueError, match="Discount exceeds subtotal"):
        await agent.execute({
            "operation": "invoice_total",
            "items": [{"name": "X", "quantity": 1, "unit_price": "100"}],
            "discount": "200",
            "gst_rate": "18",
        })


@pytest.mark.asyncio
async def test_invalid_operation(agent):
    with pytest.raises(ValueError, match="Unknown operation"):
        await agent.execute({"operation": "nonexistent"})


# ── REST Integration ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rest_gst_execution(client):
    """GST works through REST gateway."""
    response = await client.post(
        "/api/v1/agents/gst-calculator/execute",
        json={"input": {
            "operation": "calculate_gst",
            "amount": "1000",
            "gst_rate": "18",
        }},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["gst_amount"] == "180.00"
    assert data["agent"] == "gst-calculator"
    assert data["version"] == "1.0.0"


# ── MCP Integration ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mcp_gst_discovery(client):
    """GST appears in MCP tools list."""
    response = await client.get("/mcp/tools")
    assert response.status_code == 200
    slugs = [t["name"] for t in response.json()["tools"]]
    assert "gst-calculator" in slugs


@pytest.mark.asyncio
async def test_mcp_gst_execution(client):
    """GST works through MCP tools/call."""
    response = await client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "gst-calculator",
            "arguments": {
                "operation": "extract_gst",
                "amount": "1180",
                "gst_rate": "18",
            },
        },
    })
    assert response.status_code == 200
    result = json.loads(response.json()["result"]["content"][0]["text"])
    assert result["base_amount"] == "1000.00"
    assert result["gst_amount"] == "180.00"
