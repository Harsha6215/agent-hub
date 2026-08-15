"""
EMI / Loan Calculator Agent.

Operations:
  - calculate_emi: Monthly EMI from principal, annual rate, tenure
  - loan_summary: Total interest, total payment, effective cost
  - amortization: Month-by-month breakdown (first N months)
  - loan_eligibility: Max loan from monthly income
  - compare_loans: Side-by-side comparison of two loan options
  - prepayment: Impact of a lump-sum prepayment

EMI formula: P × r × (1+r)^n / ((1+r)^n - 1)
  where r = monthly rate, n = total months

Special case: when rate = 0, EMI = P / n (avoids division by zero).

All monetary values use Decimal. Returns string representations.
"""

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Any

from agents.base import BaseAgent


def _d(value: Any) -> Decimal:
    """Convert to Decimal."""
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Invalid numeric value: {value}")


def _fmt(d: Decimal) -> str:
    """Format to 2 decimal places."""
    return str(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _calculate_emi(principal: Decimal, annual_rate: Decimal, tenure_years: Decimal) -> Decimal:
    """
    Core EMI calculation.

    Returns monthly EMI.
    Handles zero-interest case (simple division).
    """
    months = tenure_years * 12

    if months <= 0:
        raise ValueError("tenure_years must be greater than 0")
    if principal <= 0:
        raise ValueError("principal must be greater than 0")
    if annual_rate < 0:
        raise ValueError("annual_rate must be non-negative")

    # Zero interest: simple division
    if annual_rate == 0:
        return principal / months

    # Monthly rate
    r = annual_rate / Decimal("1200")  # annual% / 12 / 100

    # (1+r)^n
    power = (1 + r) ** int(months)

    # EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    emi = principal * r * power / (power - 1)
    return emi


class EMICalculatorAgent(BaseAgent):
    """Loan/EMI calculator with multiple operations."""

    @property
    def name(self) -> str:
        return "Loan/EMI Calculator"

    @property
    def slug(self) -> str:
        return "emi-calculator"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Calculate EMI, total interest, amortization schedule, loan eligibility, and compare loan options."

    @property
    def category(self) -> str:
        return "finance"

    @property
    def price_per_request(self) -> int:
        return 15  # 15 paisa = ₹0.15

    def get_input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [
                        "calculate_emi",
                        "loan_summary",
                        "amortization",
                        "loan_eligibility",
                        "compare_loans",
                        "prepayment",
                    ],
                    "description": "Loan calculation to perform",
                },
                "principal": {"type": "string", "description": "Loan amount"},
                "annual_rate": {"type": "string", "description": "Annual interest rate (%)"},
                "tenure_years": {"type": "string", "description": "Loan tenure in years"},
                "months_to_show": {"type": "integer", "description": "Months for amortization (default 12)"},
                "monthly_income": {"type": "string", "description": "Monthly income (for eligibility)"},
                "max_emi_percent": {"type": "string", "description": "Max EMI as % of income (default 40)"},
                "loan_a": {"type": "object", "description": "First loan option (for compare)"},
                "loan_b": {"type": "object", "description": "Second loan option (for compare)"},
                "prepayment_amount": {"type": "string", "description": "Lump sum prepayment"},
                "prepayment_after_months": {"type": "integer", "description": "Prepay after N months"},
            },
            "required": ["operation"],
        }

    def get_output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {"type": "string"},
                "result": {"type": "object"},
            },
        }

    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        operation = input_data.get("operation")

        if operation == "calculate_emi":
            return self._calculate_emi(input_data)
        elif operation == "loan_summary":
            return self._loan_summary(input_data)
        elif operation == "amortization":
            return self._amortization(input_data)
        elif operation == "loan_eligibility":
            return self._loan_eligibility(input_data)
        elif operation == "compare_loans":
            return self._compare_loans(input_data)
        elif operation == "prepayment":
            return self._prepayment(input_data)
        else:
            raise ValueError(
                f"Unknown operation: '{operation}'. "
                f"Available: calculate_emi, loan_summary, amortization, "
                f"loan_eligibility, compare_loans, prepayment"
            )

    def _calculate_emi(self, data: dict) -> dict:
        """Basic EMI calculation."""
        principal = _d(data.get("principal", 0))
        rate = _d(data.get("annual_rate", 0))
        tenure = _d(data.get("tenure_years", 0))

        emi = _calculate_emi(principal, rate, tenure)

        return {
            "operation": "calculate_emi",
            "principal": _fmt(principal),
            "annual_rate": _fmt(rate),
            "tenure_years": str(tenure),
            "tenure_months": str(int(tenure * 12)),
            "monthly_emi": _fmt(emi),
        }

    def _loan_summary(self, data: dict) -> dict:
        """EMI + total interest + total payment."""
        principal = _d(data.get("principal", 0))
        rate = _d(data.get("annual_rate", 0))
        tenure = _d(data.get("tenure_years", 0))

        emi = _calculate_emi(principal, rate, tenure)
        months = int(tenure * 12)
        total_payment = emi * months
        total_interest = total_payment - principal
        interest_to_principal_ratio = (
            (total_interest / principal * 100) if principal > 0 else Decimal("0")
        )

        return {
            "operation": "loan_summary",
            "principal": _fmt(principal),
            "annual_rate": _fmt(rate),
            "tenure_years": str(tenure),
            "monthly_emi": _fmt(emi),
            "total_interest": _fmt(total_interest),
            "total_payment": _fmt(total_payment),
            "interest_to_principal_percent": _fmt(interest_to_principal_ratio),
        }

    def _amortization(self, data: dict) -> dict:
        """Month-by-month breakdown."""
        principal = _d(data.get("principal", 0))
        rate = _d(data.get("annual_rate", 0))
        tenure = _d(data.get("tenure_years", 0))
        months_to_show = int(data.get("months_to_show", 12))

        emi = _calculate_emi(principal, rate, tenure)
        monthly_rate = rate / Decimal("1200") if rate > 0 else Decimal("0")
        balance = principal
        schedule = []

        total_months = int(tenure * 12)
        show = min(months_to_show, total_months)

        for month in range(1, show + 1):
            interest_component = balance * monthly_rate
            principal_component = emi - interest_component
            balance = balance - principal_component

            schedule.append({
                "month": month,
                "emi": _fmt(emi),
                "principal": _fmt(principal_component),
                "interest": _fmt(interest_component),
                "balance": _fmt(max(balance, Decimal("0"))),
            })

        return {
            "operation": "amortization",
            "monthly_emi": _fmt(emi),
            "months_shown": show,
            "total_months": total_months,
            "schedule": schedule,
        }

    def _loan_eligibility(self, data: dict) -> dict:
        """Estimate max loan from income."""
        monthly_income = _d(data.get("monthly_income", 0))
        max_emi_pct = _d(data.get("max_emi_percent", "40"))
        rate = _d(data.get("annual_rate", "8.5"))
        tenure = _d(data.get("tenure_years", "20"))

        if monthly_income <= 0:
            raise ValueError("monthly_income must be greater than 0")

        max_emi = monthly_income * max_emi_pct / Decimal("100")

        # Reverse EMI formula: P = EMI * ((1+r)^n - 1) / (r * (1+r)^n)
        months = int(tenure * 12)

        if rate == 0:
            max_loan = max_emi * months
        else:
            r = rate / Decimal("1200")
            power = (1 + r) ** months
            max_loan = max_emi * (power - 1) / (r * power)

        return {
            "operation": "loan_eligibility",
            "monthly_income": _fmt(monthly_income),
            "max_emi_percent": _fmt(max_emi_pct),
            "max_emi": _fmt(max_emi),
            "annual_rate": _fmt(rate),
            "tenure_years": str(tenure),
            "estimated_max_loan": _fmt(max_loan),
        }

    def _compare_loans(self, data: dict) -> dict:
        """Compare two loan options side by side."""
        loan_a = data.get("loan_a", {})
        loan_b = data.get("loan_b", {})

        if not loan_a or not loan_b:
            raise ValueError("Both loan_a and loan_b are required")

        def calc(loan: dict) -> dict:
            p = _d(loan.get("principal", 0))
            r = _d(loan.get("annual_rate", 0))
            t = _d(loan.get("tenure_years", 0))
            emi = _calculate_emi(p, r, t)
            months = int(t * 12)
            total = emi * months
            interest = total - p
            return {
                "principal": _fmt(p),
                "annual_rate": _fmt(r),
                "tenure_years": str(t),
                "monthly_emi": _fmt(emi),
                "total_interest": _fmt(interest),
                "total_payment": _fmt(total),
            }

        a = calc(loan_a)
        b = calc(loan_b)

        # Determine which saves more
        total_a = _d(a["total_payment"])
        total_b = _d(b["total_payment"])
        savings = abs(total_a - total_b)
        cheaper = "loan_a" if total_a < total_b else "loan_b" if total_b < total_a else "equal"

        return {
            "operation": "compare_loans",
            "loan_a": a,
            "loan_b": b,
            "cheaper_option": cheaper,
            "savings": _fmt(savings),
        }

    def _prepayment(self, data: dict) -> dict:
        """Impact of a lump-sum prepayment."""
        principal = _d(data.get("principal", 0))
        rate = _d(data.get("annual_rate", 0))
        tenure = _d(data.get("tenure_years", 0))
        prepay_amount = _d(data.get("prepayment_amount", 0))
        prepay_after = int(data.get("prepayment_after_months", 12))

        if prepay_amount <= 0:
            raise ValueError("prepayment_amount must be greater than 0")
        if prepay_after <= 0:
            raise ValueError("prepayment_after_months must be greater than 0")

        emi = _calculate_emi(principal, rate, tenure)
        monthly_rate = rate / Decimal("1200") if rate > 0 else Decimal("0")
        total_months = int(tenure * 12)

        # Calculate balance at prepayment point
        balance = principal
        for _ in range(prepay_after):
            interest = balance * monthly_rate
            principal_paid = emi - interest
            balance -= principal_paid

        # After prepayment
        new_balance = balance - prepay_amount
        if new_balance <= 0:
            return {
                "operation": "prepayment",
                "message": "Prepayment fully clears the remaining loan",
                "original_emi": _fmt(emi),
                "balance_at_prepayment": _fmt(balance),
                "prepayment_amount": _fmt(prepay_amount),
            }

        # New EMI with same tenure remaining
        remaining_months = total_months - prepay_after
        remaining_years = Decimal(remaining_months) / Decimal("12")
        new_emi = _calculate_emi(new_balance, rate, remaining_years)

        # Savings
        original_total = emi * total_months
        new_total = (emi * prepay_after) + prepay_amount + (new_emi * remaining_months)
        savings = original_total - new_total

        return {
            "operation": "prepayment",
            "original_emi": _fmt(emi),
            "balance_at_prepayment": _fmt(balance),
            "prepayment_amount": _fmt(prepay_amount),
            "new_balance": _fmt(new_balance),
            "new_emi": _fmt(new_emi),
            "interest_savings": _fmt(savings),
        }
