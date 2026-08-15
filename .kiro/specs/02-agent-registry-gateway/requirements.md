# Epic 2 — Agent Registry + API Gateway: Requirements

## Overview
Build the agent registration system and API gateway that routes requests to the correct agent. Every future agent plugs into this same infrastructure.

## Business Context
- Agents are products — each one has a lifecycle, pricing, versioning, and documentation
- The API Gateway is the single entry point for all agent executions
- Adding a new revenue-generating agent should be trivial once this epic is done

## Functional Requirements

### FR-1: Agent Model & CRUD
- Agent table with: name, slug, description, category, version, status, pricing, rate_limit
- Agent statuses: `draft`, `active`, `paused`, `deprecated`
- Admin CRUD: create, read, update, delete agents
- Public read: list active agents, get agent by slug

### FR-2: Agent Categories
- Finance, Business, Career, Data, Utility
- Filterable by category in the registry

### FR-3: Agent Registry API
```
POST   /api/v1/agents          (admin) Create agent
GET    /api/v1/agents          (public) List active agents
GET    /api/v1/agents/{slug}   (public) Get agent details
PUT    /api/v1/agents/{id}     (admin) Update agent
DELETE /api/v1/agents/{id}     (admin) Delete agent
```

### FR-4: API Gateway
- Single execution endpoint: `POST /api/v1/agents/{slug}/execute`
- Gateway flow:
  1. Validate API key (Authorization: Bearer sk_live_xxx)
  2. Look up agent by slug
  3. Verify agent is active
  4. Validate input against agent's schema
  5. Execute agent logic
  6. Return standardized response
  7. Record usage event

### FR-5: BaseAgent Interface
- Abstract base class that all agents inherit from
- Methods: `validate_input()`, `execute()`, `get_schema()`
- Properties: name, version, description, category, input_schema, output_schema
- Agents register themselves into a global registry on startup

### FR-6: Agent Input/Output Contract
- Every agent has Pydantic input and output schemas
- Input validation happens at gateway level
- Output is always wrapped in standard response format

### FR-7: Agent Versioning
- URL includes version: `/api/v1/agents/{slug}/execute` (agent's internal version tracked)
- Never break existing API contract without version bump

### FR-8: Agent Execution Logs
- Every execution recorded: agent_id, request_id, status, latency, timestamp
- Do not store sensitive user inputs

### FR-9: Agent Documentation (Auto-generated)
- `GET /api/v1/agents/{slug}/docs` returns agent documentation
- Includes: description, input schema, output schema, examples, pricing, rate limits

### FR-10: Frontend — Agent Catalog Page
- List all active agents with: name, category, description, pricing
- Click to view agent detail page with documentation
- Search/filter by category

## Non-Functional Requirements
- Agent lookup < 10ms (Redis cache)
- Gateway overhead < 20ms
- Agent registry refreshes automatically when agents are updated

## Acceptance Criteria
- [ ] Can register a new agent via API
- [ ] Agent appears in public registry
- [ ] Can execute agent via gateway endpoint
- [ ] Input validation works against schema
- [ ] Execution is recorded in usage_events
- [ ] Agent documentation is auto-generated
- [ ] Frontend shows agent catalog
- [ ] Invalid/inactive agent returns proper error
