# Agents

This directory contains all agent implementations for the Agent Hub platform.

## Creating a New Agent

Each agent lives in its own subdirectory and inherits from `BaseAgent`.

### Structure
```
agents/
├── base.py              # BaseAgent abstract class
├── hello/
│   ├── __init__.py
│   └── agent.py         # HelloAgent implementation
├── gst_calculator/
│   ├── __init__.py
│   └── agent.py         # GSTCalculatorAgent
└── ...
```

### Template

```python
from agents.base import BaseAgent
from pydantic import BaseModel


class MyInput(BaseModel):
    """Input schema — validated before execution."""
    value: str


class MyOutput(BaseModel):
    """Output schema — returned to the caller."""
    result: str


class MyAgent(BaseAgent):
    name = "My Agent"
    slug = "my-agent"
    version = "1.0"
    description = "Does something useful."
    category = "utility"

    def get_input_schema(self):
        return MyInput

    def get_output_schema(self):
        return MyOutput

    async def execute(self, input_data: MyInput) -> MyOutput:
        return MyOutput(result=f"Processed: {input_data.value}")
```

### Registration
Agents are auto-discovered on startup. Just create the directory and implement the class.

### Pricing
Set pricing in the agent's database record:
- `pricing_model`: "per_request" or "subscription"
- `price_per_request`: amount in INR (e.g., 0.10 = ₹0.10 per call)
