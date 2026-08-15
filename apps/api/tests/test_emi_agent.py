"""
Tests for EMI/Loan Calculator Agent.
Covers: EMI formula, zero-interest, amortization, prepayment,
comparison, validation, rounding, boundary, REST, MCP.
"""

import json
from decimal import Decimal

import pytest
from agents.emi.agent import EMICalculatorAgent


@pytest.fixture
def agent():
    return EMICalculatorAgent()


# ── Metadata ───────────────────────────────────────────────────────────────────

def test_emi_metadata(agent):
    assert agent.slug == "emi-calculator"
    assert agent.name == "Loan/EMI Calculator"
    assert agent.version == "1.0.0"
    assert agent.category == "finance"
    assert agent.price_per_request == 15


# ── EMI Formula Tests ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_emi_reference_case(agent):
    """
    Reference: ₹5,00,000 at 8.5% for 20 years.
    Expected EMI roughly ₹4,300–₹4,400/month.
    """
    result = await agent.execute({
        "operation": "calculate_emi",
        "principal": "500000",
        "annual_rate": "8.5",
        "tenure_years": "20",
    })
    emi = Decimal(result["monthly_emi"])
    assert Decimal("4300") <= emi <= Decimal("4400"), f"EMI {emi} not in expected range"


@pytest.mark.asyncio
async def test_emi_standard_home_loan(agent):
    """₹50,00,000 at 8.5% for 20 years → EMI ~₹43,391."""
    result = await agent.execute({
        "operation": "calculate_emi",
        "principal": "5000000",
        "annual_rate": "8.5",
        "tenure_years": "20",
    })
    emi = Decimal(result["monthly_emi"])
    # Should be roughly 43,000-44,000
    assert Decimal("43000") <= emi <= Decimal("44000")


@pytest.mark.asyncio
async def test_emi_short_tenure(agent):
    """₹1,00,000 at 10% for 1 year → EMI ~₹8,792."""
    result = await agent.execute({
        "operation": "calculate_emi",
        "principal": "100000",
        "annual_rate": "10",
        "tenure_years": "1",
    })
    emi = Decimal(result["monthly_emi"])
    assert Decimal("8700") <= emi <= Decimal("8900")


# ── Zero Interest ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_emi_zero_interest(agent):
    """0% interest: EMI = principal / months (no division by zero)."""
    result = await agent.execute({
        "operation": "calculate_emi",
        "principal": "120000",
        "annual_rate": "0",
        "tenure_years": "1",
    })
    # 120000 / 12 = 10000
    assert result["monthly_emi"] == "10000.00"


@pytest.mark.asyncio
async def test_loan_summary_zero_interest(agent):
    """Zero interest: total interest = 0."""
    result = await agent.execute({
        "operation": "loan_summary",
        "principal": "120000",
        "annual_rate": "0",
        "tenure_years": "1",
    })
    assert result["total_interest"] == "0.00"
    assert result["total_payment"] == "120000.00"


# ── Loan Summary ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_loan_summary(agent):
    """Full summary with interest ratio."""
    result = await agent.execute({
        "operation": "loan_summary",
        "principal": "1000000",
        "annual_rate": "8.5",
        "tenure_years": "20",
    })
    assert "monthly_emi" in result
    assert "total_interest" in result
    assert "total_payment" in result
    assert "interest_to_principal_percent" in result
    # Total payment > principal
    assert Decimal(result["total_payment"]) > Decimal("1000000")


# ── Amortization ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_amortization_basic(agent):
    """Amortization returns monthly schedule."""
    result = await agent.execute({
        "operation": "amortization",
        "principal": "100000",
        "annual_rate": "12",
        "tenure_years": "1",
        "months_to_show": 3,
    })
    assert result["months_shown"] == 3
    assert result["total_months"] == 12
    assert len(result["schedule"]) == 3

    # First month: interest should be highest
    first = result["schedule"][0]
    assert first["month"] == 1
    assert "emi" in first
    assert "principal" in first
    assert "interest" in first
    assert "balance" in first


@pytest.mark.asyncio
async def test_amortization_balance_decreases(agent):
    """Balance should decrease each month."""
    result = await agent.execute({
        "operation": "amortization",
        "principal": "500000",
        "annual_rate": "10",
        "tenure_years": "5",
        "months_to_show": 6,
    })
    balances = [Decimal(m["balance"]) for m in result["schedule"]]
    for i in range(1, len(balances)):
        assert balances[i] < balances[i - 1]


# ── Loan Eligibility ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_loan_eligibility(agent):
    """Income ₹50,000 at 40% EMI cap → max EMI ₹20,000."""
    result = await agent.execute({
        "operation": "loan_eligibility",
        "monthly_income": "50000",
        "max_emi_percent": "40",
        "annual_rate": "8.5",
        "tenure_years": "20",
    })
    assert result["max_emi"] == "20000.00"
    max_loan = Decimal(result["estimated_max_loan"])
    # At 8.5% for 20 years, ₹20k EMI supports roughly ₹23L loan
    assert max_loan > Decimal("2000000")


@pytest.mark.asyncio
async def test_eligibility_zero_rate(agent):
    """Zero rate eligibility: max_loan = max_emi * months."""
    result = await agent.execute({
        "operation": "loan_eligibility",
        "monthly_income": "100000",
        "max_emi_percent": "50",
        "annual_rate": "0",
        "tenure_years": "10",
    })
    # max_emi = 50000, months = 120 → max_loan = 6000000
    assert result["estimated_max_loan"] == "6000000.00"


# ── Compare Loans ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_compare_loans(agent):
    """Compare: shorter tenure = less total interest."""
    result = await agent.execute({
        "operation": "compare_loans",
        "loan_a": {"principal": "1000000", "annual_rate": "8.5", "tenure_years": "20"},
        "loan_b": {"principal": "1000000", "annual_rate": "8.5", "tenure_years": "15"},
    })
    assert result["cheaper_option"] == "loan_b"
    savings = Decimal(result["savings"])
    assert savings > 0


@pytest.mark.asyncio
async def test_compare_same_loan(agent):
    """Same loans = equal."""
    result = await agent.execute({
        "operation": "compare_loans",
        "loan_a": {"principal": "500000", "annual_rate": "9", "tenure_years": "10"},
        "loan_b": {"principal": "500000", "annual_rate": "9", "tenure_years": "10"},
    })
    assert result["cheaper_option"] == "equal"


# ── Prepayment ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_prepayment_reduces_emi(agent):
    """Prepayment should reduce new EMI."""
    result = await agent.execute({
        "operation": "prepayment",
        "principal": "1000000",
        "annual_rate": "8.5",
        "tenure_years": "20",
        "prepayment_amount": "200000",
        "prepayment_after_months": 24,
    })
    original = Decimal(result["original_emi"])
    new = Decimal(result["new_emi"])
    assert new < original
    assert Decimal(result["interest_savings"]) > 0


@pytest.mark.asyncio
async def test_prepayment_clears_loan(agent):
    """Large prepayment can fully clear the loan."""
    result = await agent.execute({
        "operation": "prepayment",
        "principal": "100000",
        "annual_rate": "10",
        "tenure_years": "5",
        "prepayment_amount": "200000",
        "prepayment_after_months": 6,
    })
    assert "fully clears" in result["message"]


# ── Validation ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_negative_principal(agent):
    with pytest.raises(ValueError, match="principal must be greater than 0"):
        await agent.execute({
            "operation": "calculate_emi",
            "principal": "-100000",
            "annual_rate": "10",
            "tenure_years": "5",
        })


@pytest.mark.asyncio
async def test_zero_tenure(agent):
    with pytest.raises(ValueError, match="tenure_years must be greater than 0"):
        await agent.execute({
            "operation": "calculate_emi",
            "principal": "100000",
            "annual_rate": "10",
            "tenure_years": "0",
        })


@pytest.mark.asyncio
async def test_negative_rate(agent):
    with pytest.raises(ValueError, match="annual_rate must be non-negative"):
        await agent.execute({
            "operation": "calculate_emi",
            "principal": "100000",
            "annual_rate": "-5",
            "tenure_years": "5",
        })


@pytest.mark.asyncio
async def test_invalid_operation(agent):
    with pytest.raises(ValueError, match="Unknown operation"):
        await agent.execute({"operation": "nonexistent"})


@pytest.mark.asyncio
async def test_compare_missing_loan(agent):
    with pytest.raises(ValueError, match="Both loan_a and loan_b are required"):
        await agent.execute({"operation": "compare_loans", "loan_a": {}})


# ── Rounding / Precision ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rounding_consistency(agent):
    """EMI rounded to 2 decimal places."""
    result = await agent.execute({
        "operation": "calculate_emi",
        "principal": "333333",
        "annual_rate": "7.75",
        "tenure_years": "15",
    })
    emi = result["monthly_emi"]
    # Should have exactly 2 decimal places
    assert "." in emi
    assert len(emi.split(".")[1]) == 2


# ── REST Integration ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rest_emi_execution(client):
    """EMI works through REST gateway."""
    response = await client.post(
        "/api/v1/agents/emi-calculator/execute",
        json={"input": {
            "operation": "calculate_emi",
            "principal": "500000",
            "annual_rate": "8.5",
            "tenure_years": "20",
        }},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["agent"] == "emi-calculator"
    assert data["version"] == "1.0.0"
    emi = Decimal(data["data"]["monthly_emi"])
    assert Decimal("4300") <= emi <= Decimal("4400")


# ── MCP Integration ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mcp_emi_discovery(client):
    """EMI appears in MCP tools list."""
    response = await client.get("/mcp/tools")
    slugs = [t["name"] for t in response.json()["tools"]]
    assert "emi-calculator" in slugs


@pytest.mark.asyncio
async def test_mcp_emi_execution(client):
    """EMI works through MCP tools/call."""
    response = await client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "emi-calculator",
            "arguments": {
                "operation": "loan_summary",
                "principal": "1000000",
                "annual_rate": "8.5",
                "tenure_years": "20",
            },
        },
    })
    assert response.status_code == 200
    result = json.loads(response.json()["result"]["content"][0]["text"])
    assert Decimal(result["total_payment"]) > Decimal("1000000")
    assert Decimal(result["total_interest"]) > 0
