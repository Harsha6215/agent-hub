# Epic 5 — First Revenue Agents: Design

## Architecture Decision: MCP Through Gateway

### Current Flow (Epic 4)
```
MCP tools/call → agent.execute() directly (no auth, no usage, no billing)
```

### New Flow (Epic 5)
```
MCP tools/call
    ↓
MCP Adapter (apps/api/app/mcp/server.py)
    ↓
Gateway Execution Logic (shared with REST)
    ↓
Authentication (API key from MCP request metadata)
    ↓
Rate Limiting
    ↓
Agent Execution
    ↓
Usage Recording
    ↓
Response (formatted as MCP content)
```

### Implementation
- Extract gateway execution logic into a shared service: `apps/api/app/services/executor.py`
- Both REST gateway endpoint AND MCP tools/call use the same executor
- Executor handles: auth → rate limit → execute → record usage → return result
- MCP can pass API key via request params or remain unauthenticated for free-tier agents

## Agent Directory Structure

```
agents/
├── base.py                    # BaseAgent ABC
├── hello/                     # Demo agent (existing)
│   └── agent.py
├── business/                  # Business Calculator
│   └── agent.py
├── gst/                       # GST Calculator
│   └── agent.py
└── emi/                       # EMI/Loan Calculator
    └── agent.py
```

Each agent folder contains ONE file: `agent.py` with a class that extends BaseAgent.
No `__init__.py` needed in agent folders (auto-discovery scans for `agent.py`).

## Agent Design Pattern

```python
class BusinessCalculatorAgent(BaseAgent):
    @property
    def name(self) -> str: return "Business Calculator"

    @property
    def slug(self) -> str: return "business-calculator"

    @property
    def price_per_request(self) -> int: return 10  # 10 paisa = ₹0.10

    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": [...]},
                ...values...
            },
            "required": ["operation"]
        }

    async def execute(self, input_data: dict) -> dict:
        operation = input_data["operation"]
        # Route to appropriate calculation
        # Return structured result
```

## Shared Executor Service

```python
# apps/api/app/services/executor.py

async def execute_agent(
    slug: str,
    input_data: dict,
    api_key: str | None = None,
    request_id: str = "unknown",
) -> ExecutionResult:
    """
    Unified execution path for both REST and MCP.
    
    1. Lookup agent in registry
    2. Authenticate (if api_key provided or production mode)
    3. Rate limit check
    4. Validate input
    5. Execute agent
    6. Record usage
    7. Return result
    """
```

## Pricing Model (metadata only)

| Agent | Price | Justification |
|-------|-------|---------------|
| hello | 0 paisa | Demo, always free |
| business-calculator | 10 paisa (₹0.10) | Simple calculation |
| gst-calculator | 10 paisa (₹0.10) | Simple calculation |
| emi-calculator | 15 paisa (₹0.15) | Slightly more complex (amortization) |

No payment collection in Epic 5. Pricing is recorded in usage events for future billing.

## Input/Output Conventions

All agents follow:
- Input: JSON object with `operation` field (for multi-function agents) or direct fields
- Output: JSON object with `result` field containing the calculation
- Errors: Raise `ValueError` with clear message for invalid inputs
- Numbers: Use float for monetary values, round to 2 decimal places

## Test Strategy

Each agent gets:
1. Unit test for each operation (correct math)
2. Edge cases (zero values, negative numbers, boundary conditions)
3. Invalid input rejection
4. Integration test via REST gateway
5. Integration test via MCP tools/call

## Files to Create/Modify

### New Files
- `agents/business/agent.py` — Business Calculator
- `agents/gst/agent.py` — GST Calculator
- `agents/emi/agent.py` — EMI Calculator
- `apps/api/app/services/executor.py` — Shared execution logic
- `apps/api/tests/test_business_agent.py`
- `apps/api/tests/test_gst_agent.py`
- `apps/api/tests/test_emi_agent.py`

### Modified Files
- `apps/api/app/mcp/server.py` — Route through executor
- `apps/api/app/api/v1/gateway.py` — Use shared executor
- `agents/__init__.py` — No changes needed (auto-discovery handles it)
