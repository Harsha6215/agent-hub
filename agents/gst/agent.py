"""
GST Calculator Agent — forward GST, reverse GST, invoice total.

All calculations use Decimal for precision.
Supported GST rates: 0%, 5%, 12%, 18%, 28%.

Rounding rule: All monetary values rounded to 2 decimal places (ROUND_HALF_UP).
Note on reverse calculation: extracting base from GST-inclusive price may not
produce the exact original due to rounding. This is standard financial behaviour.
The agent documents its rounding rather than pretending exactness.
"""

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Any

from agents.base import BaseAgent

VALID_GST_RATES = [Decimal("0"), Decimal("5"), Decimal("12"), Decimal("18"), Decimal("28")]


def _d(value: Any) -> Decimal:
    """Convert input to Decimal."""
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Invalid numeric value: {value}")


def _fmt(d: Decimal) -> str:
    """Format to 2 decimal places."""
    return str(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


class GSTCalculatorAgent(BaseAgent):
    """Indian GST calculator with forward, reverse, and invoice operations."""

    @property
    def name(self) -> str:
        return "GST Calculator"

    @property
    def slug(self) -> str:
        return "gst-calculator"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Calculate Indian GST — forward (add GST), reverse (extract GST from inclusive price), and invoice totals."

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
                    "enum": ["calculate_gst", "extract_gst", "invoice_total"],
                    "description": "GST operation to perform",
                },
                "amount": {
                    "type": "string",
                    "description": "Base amount (for calculate_gst) or inclusive amount (for extract_gst)",
                },
                "gst_rate": {
                    "type": "string",
                    "description": "GST rate: 0, 5, 12, 18, or 28",
                },
                "is_interstate": {
                    "type": "boolean",
                    "description": "True for IGST (inter-state), False for CGST+SGST (intra-state). Default: false",
                },
                "items": {
                    "type": "array",
                    "description": "Invoice line items (for invoice_total)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "quantity": {"type": "number"},
                            "unit_price": {"type": "string"},
                        },
                    },
                },
                "discount": {
                    "type": "string",
                    "description": "Flat discount on subtotal (for invoice_total)",
                },
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

        if operation == "calculate_gst":
            return self._calculate_gst(input_data)
        elif operation == "extract_gst":
            return self._extract_gst(input_data)
        elif operation == "invoice_total":
            return self._invoice_total(input_data)
        else:
            raise ValueError(
                f"Unknown operation: '{operation}'. "
                f"Available: calculate_gst, extract_gst, invoice_total"
            )

    def _validate_rate(self, rate: Decimal) -> None:
        if rate not in VALID_GST_RATES:
            raise ValueError(
                f"Invalid GST rate: {rate}%. Valid rates: 0, 5, 12, 18, 28"
            )

    def _calculate_gst(self, data: dict) -> dict:
        """Forward: add GST to base amount."""
        amount = _d(data.get("amount", 0))
        rate = _d(data.get("gst_rate", 18))
        is_interstate = data.get("is_interstate", False)

        if amount < 0:
            raise ValueError("amount must be non-negative")
        self._validate_rate(rate)

        gst_amount = amount * rate / Decimal("100")
        total = amount + gst_amount

        result = {
            "operation": "calculate_gst",
            "base_amount": _fmt(amount),
            "gst_rate": _fmt(rate),
            "gst_amount": _fmt(gst_amount),
            "total_amount": _fmt(total),
        }

        if is_interstate:
            result["igst"] = _fmt(gst_amount)
        else:
            half = gst_amount / Decimal("2")
            result["cgst"] = _fmt(half)
            result["sgst"] = _fmt(half)

        return result

    def _extract_gst(self, data: dict) -> dict:
        """
        Reverse: extract base amount from GST-inclusive price.

        Formula: base = inclusive / (1 + rate/100)

        Note: Due to rounding, base + GST may not exactly equal the inclusive
        amount. This is standard financial rounding behaviour.
        """
        inclusive = _d(data.get("amount", 0))
        rate = _d(data.get("gst_rate", 18))
        is_interstate = data.get("is_interstate", False)

        if inclusive < 0:
            raise ValueError("amount must be non-negative")
        self._validate_rate(rate)

        divisor = Decimal("1") + rate / Decimal("100")
        base_amount = inclusive / divisor
        gst_amount = inclusive - base_amount

        result = {
            "operation": "extract_gst",
            "inclusive_amount": _fmt(inclusive),
            "gst_rate": _fmt(rate),
            "base_amount": _fmt(base_amount),
            "gst_amount": _fmt(gst_amount),
            "rounding_note": "Reverse calculation uses ROUND_HALF_UP. Base + GST may differ from inclusive by ±0.01 due to rounding.",
        }

        if is_interstate:
            result["igst"] = _fmt(gst_amount)
        else:
            half = gst_amount / Decimal("2")
            result["cgst"] = _fmt(half)
            result["sgst"] = _fmt(half)

        return result

    def _invoice_total(self, data: dict) -> dict:
        """
        Calculate invoice total from line items.

        Flow: Subtotal → Discount → Taxable Value → GST → Grand Total
        """
        items = data.get("items", [])
        discount = _d(data.get("discount", "0"))
        rate = _d(data.get("gst_rate", 18))
        is_interstate = data.get("is_interstate", False)

        if not items:
            raise ValueError("items array is required and must not be empty")
        self._validate_rate(rate)
        if discount < 0:
            raise ValueError("discount must be non-negative")

        # Calculate subtotal
        subtotal = Decimal("0")
        line_items = []
        for item in items:
            name = item.get("name", "Item")
            qty = _d(item.get("quantity", 1))
            unit_price = _d(item.get("unit_price", 0))
            line_total = qty * unit_price
            subtotal += line_total
            line_items.append({
                "name": name,
                "quantity": str(qty),
                "unit_price": _fmt(unit_price),
                "line_total": _fmt(line_total),
            })

        taxable_value = subtotal - discount
        if taxable_value < 0:
            raise ValueError("Discount exceeds subtotal")

        gst_amount = taxable_value * rate / Decimal("100")
        grand_total = taxable_value + gst_amount

        result = {
            "operation": "invoice_total",
            "items": line_items,
            "subtotal": _fmt(subtotal),
            "discount": _fmt(discount),
            "taxable_value": _fmt(taxable_value),
            "gst_rate": _fmt(rate),
            "gst_amount": _fmt(gst_amount),
            "grand_total": _fmt(grand_total),
        }

        if is_interstate:
            result["igst"] = _fmt(gst_amount)
        else:
            half = gst_amount / Decimal("2")
            result["cgst"] = _fmt(half)
            result["sgst"] = _fmt(half)

        return result
