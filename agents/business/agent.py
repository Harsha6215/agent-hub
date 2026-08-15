"""
Business Calculator Agent — profit, margin, markup, break-even, discount.

All monetary calculations use Decimal for precision.
Returns string representations of numbers (e.g., "250.00") — never floats.
"""

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Any

from agents.base import BaseAgent


def _d(value: Any) -> Decimal:
    """Convert input to Decimal. Raises ValueError on failure."""
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Invalid numeric value: {value}")


def _fmt(d: Decimal, places: int = 2) -> str:
    """Format Decimal to string with fixed decimal places."""
    return str(d.quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP))


class BusinessCalculatorAgent(BaseAgent):
    """Multi-operation business calculator."""

    @property
    def name(self) -> str:
        return "Business Calculator"

    @property
    def slug(self) -> str:
        return "business-calculator"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Calculate profit, margin, markup, break-even point, and discounts for business decisions."

    @property
    def category(self) -> str:
        return "finance"

    @property
    def price_per_request(self) -> int:
        return 10  # 10 paisa = ₹0.10

    def get_input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [
                        "profit",
                        "margin",
                        "markup",
                        "breakeven",
                        "discount",
                    ],
                    "description": "Calculation to perform",
                },
                "cost": {"type": "string", "description": "Cost/purchase price"},
                "selling_price": {"type": "string", "description": "Selling price / revenue"},
                "fixed_costs": {"type": "string", "description": "Fixed costs (for breakeven)"},
                "variable_cost_per_unit": {"type": "string", "description": "Variable cost per unit (for breakeven)"},
                "price_per_unit": {"type": "string", "description": "Price per unit (for breakeven)"},
                "original_price": {"type": "string", "description": "Original price (for discount)"},
                "discount_percent": {"type": "string", "description": "Discount percentage (for discount)"},
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

        if operation == "profit":
            return self._profit(input_data)
        elif operation == "margin":
            return self._margin(input_data)
        elif operation == "markup":
            return self._markup(input_data)
        elif operation == "breakeven":
            return self._breakeven(input_data)
        elif operation == "discount":
            return self._discount(input_data)
        else:
            raise ValueError(
                f"Unknown operation: '{operation}'. "
                f"Available: profit, margin, markup, breakeven, discount"
            )

    def _profit(self, data: dict) -> dict:
        cost = _d(data.get("cost", 0))
        selling_price = _d(data.get("selling_price", 0))

        if cost < 0 or selling_price < 0:
            raise ValueError("Cost and selling_price must be non-negative")

        profit = selling_price - cost
        margin_pct = (profit / selling_price * 100) if selling_price > 0 else Decimal("0")
        markup_pct = (profit / cost * 100) if cost > 0 else Decimal("0")

        return {
            "operation": "profit",
            "cost": _fmt(cost),
            "selling_price": _fmt(selling_price),
            "profit": _fmt(profit),
            "margin_percent": _fmt(margin_pct),
            "markup_percent": _fmt(markup_pct),
        }

    def _margin(self, data: dict) -> dict:
        """Margin = (selling_price - cost) / selling_price × 100"""
        cost = _d(data.get("cost", 0))
        selling_price = _d(data.get("selling_price", 0))

        if selling_price <= 0:
            raise ValueError("selling_price must be greater than 0")

        profit = selling_price - cost
        margin = profit / selling_price * 100

        return {
            "operation": "margin",
            "selling_price": _fmt(selling_price),
            "cost": _fmt(cost),
            "profit": _fmt(profit),
            "margin_percent": _fmt(margin),
        }

    def _markup(self, data: dict) -> dict:
        """Markup = (selling_price - cost) / cost × 100"""
        cost = _d(data.get("cost", 0))
        selling_price = _d(data.get("selling_price", 0))

        if cost <= 0:
            raise ValueError("cost must be greater than 0")

        profit = selling_price - cost
        markup = profit / cost * 100

        return {
            "operation": "markup",
            "cost": _fmt(cost),
            "selling_price": _fmt(selling_price),
            "profit": _fmt(profit),
            "markup_percent": _fmt(markup),
        }

    def _breakeven(self, data: dict) -> dict:
        """Break-even units = fixed_costs / (price_per_unit - variable_cost_per_unit)"""
        fixed_costs = _d(data.get("fixed_costs", 0))
        price_per_unit = _d(data.get("price_per_unit", 0))
        variable_cost = _d(data.get("variable_cost_per_unit", 0))

        if fixed_costs < 0:
            raise ValueError("fixed_costs must be non-negative")

        contribution = price_per_unit - variable_cost
        if contribution <= 0:
            raise ValueError("price_per_unit must exceed variable_cost_per_unit")

        breakeven_units = fixed_costs / contribution
        breakeven_revenue = breakeven_units * price_per_unit

        return {
            "operation": "breakeven",
            "fixed_costs": _fmt(fixed_costs),
            "price_per_unit": _fmt(price_per_unit),
            "variable_cost_per_unit": _fmt(variable_cost),
            "contribution_per_unit": _fmt(contribution),
            "breakeven_units": _fmt(breakeven_units, 0),
            "breakeven_revenue": _fmt(breakeven_revenue),
        }

    def _discount(self, data: dict) -> dict:
        """Calculate discounted price."""
        original = _d(data.get("original_price", 0))
        discount_pct = _d(data.get("discount_percent", 0))

        if original < 0:
            raise ValueError("original_price must be non-negative")
        if discount_pct < 0 or discount_pct > 100:
            raise ValueError("discount_percent must be between 0 and 100")

        savings = original * discount_pct / 100
        final_price = original - savings

        return {
            "operation": "discount",
            "original_price": _fmt(original),
            "discount_percent": _fmt(discount_pct),
            "savings": _fmt(savings),
            "final_price": _fmt(final_price),
        }
