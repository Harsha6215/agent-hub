# Epic 2 — Agent Registry + API Gateway: Design

## Architecture

```
Client Request
    │
    ▼
┌───────────────────────────────┐
│        API Gateway            │
│  /api/v1/agents/{slug}/execute│
├───────────────────────────────┤
│  1. Parse API Key             │
│  2. Authenticate              │
│  3. Lookup Agent (Redis/DB)   │
│  4. Validate Input            │
│  5. Execute Agent             │
│  6. Format Response           │
│  7. Record Usage              │
└───────────────────────────────┘
    │
    ▼
┌───────────────────────────────┐
│        Agent Registry         │
│  ┌─────────┐ ┌─────────┐     │
│  │ GST     │ │ Salary  │     │
│  │ Agent   │ │ Agent   │ ... │
│  └─────────┘ └─────────┘     │
└───────────────────────────────┘
```

## BaseAgent Class

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel

class BaseAgent(ABC):
    name: str
    slug: str
    version: str
    description: str
    category: str

    @abstractmethod
    def get_input_schema(self) -> type[BaseModel]:
        """Return Pydantic model for input validation."""
        pass

    @abstractmethod
    def get_output_schema(self) -> type[BaseModel]:
        """Return Pydantic model for output."""
        pass

    @abstractmethod
    async def execute(self, input_data: BaseModel) -> BaseModel:
        """Execute agent logic and return result."""
        pass

    def get_documentation(self) -> dict:
        """Auto-generate documentation from schemas."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "category": self.category,
            "input_schema": self.get_input_schema().model_json_schema(),
            "output_schema": self.get_output_schema().model_json_schema(),
        }
```

## Agent Registry (In-Memory + DB)

```python
class AgentRegistry:
    """
    In-memory registry of all available agents.
    Loaded on startup, refreshable via Redis pub/sub.
    """
    _agents: dict[str, BaseAgent] = {}

    @classmethod
    def register(cls, agent: BaseAgent):
        cls._agents[agent.slug] = agent

    @classmethod
    def get(cls, slug: str) -> BaseAgent | None:
        return cls._agents.get(slug)

    @classmethod
    def list_active(cls) -> list[BaseAgent]:
        return list(cls._agents.values())
```

## Gateway Execution Flow

```python
@router.post("/agents/{slug}/execute")
async def execute_agent(
    slug: str,
    payload: dict,
    api_key: ApiKey = Depends(validate_api_key),
    db: AsyncSession = Depends(get_db),
):
    # 1. Find agent
    agent = AgentRegistry.get(slug)
    if not agent:
        raise NotFoundError(f"Agent '{slug}' not found")

    # 2. Check agent status (from DB)
    agent_record = await get_agent_by_slug(db, slug)
    if agent_record.status != "active":
        raise ValidationError(f"Agent '{slug}' is not active")

    # 3. Validate input
    input_schema = agent.get_input_schema()
    validated_input = input_schema(**payload)

    # 4. Execute
    start = time.time()
    result = await agent.execute(validated_input)
    latency_ms = int((time.time() - start) * 1000)

    # 5. Record usage
    await record_usage_event(db, api_key, agent_record, latency_ms, "success")

    # 6. Return
    return {"success": True, "data": result.model_dump(), "request_id": get_request_id()}
```

## API Response Formats

### Agent List
```json
{
  "success": true,
  "data": {
    "agents": [
      {
        "name": "GST Calculator",
        "slug": "gst-calculator",
        "description": "Calculate GST for Indian businesses",
        "category": "finance",
        "version": "1.0",
        "pricing": {"model": "per_request", "price": 0.10, "currency": "INR"},
        "rate_limit": {"requests_per_minute": 60}
      }
    ],
    "total": 1
  }
}
```

### Agent Execution
```json
{
  "success": true,
  "data": {
    "agent": "gst-calculator",
    "version": "1.0",
    "result": {
      "base_amount": 100000,
      "gst_rate": 18,
      "gst_amount": 18000,
      "total": 118000
    }
  },
  "request_id": "req_abc123",
  "latency_ms": 12
}
```

## Database Additions
- Extend `agents` table with `input_schema_json` and `output_schema_json` columns
- Add `agent_categories` enum or reference table

## File Structure (New files in Epic 2)
```
apps/api/app/
├── api/v1/
│   ├── agents.py           # Agent CRUD + execute endpoints
│   └── gateway.py          # Gateway execution logic
├── services/
│   ├── agent_registry.py   # In-memory registry
│   └── agent_executor.py   # Execution orchestration
├── schemas/
│   ├── agent.py            # Agent request/response schemas
│   └── gateway.py          # Gateway schemas

agents/
├── __init__.py
├── base.py                 # BaseAgent abstract class
└── README.md               # How to create a new agent
```

## Caching Strategy
- Agent list cached in Redis (TTL: 5 min)
- Individual agent lookup cached (TTL: 5 min)
- Cache invalidated on agent create/update/delete
