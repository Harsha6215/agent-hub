# Epic 2 — Agent Registry + API Gateway: Tasks

## Task 1: BaseAgent Abstract Class
- [ ] Create `agents/__init__.py`
- [ ] Create `agents/base.py` — BaseAgent ABC with: name, slug, version, description, category
- [ ] Implement abstract methods: `get_input_schema()`, `get_output_schema()`, `execute()`
- [ ] Implement `get_documentation()` method (auto-generates from schemas)
- [ ] Create `agents/README.md` — instructions for creating new agents

## Task 2: Agent Registry Service
- [ ] Create `apps/api/app/services/__init__.py`
- [ ] Create `apps/api/app/services/agent_registry.py` — AgentRegistry class
- [ ] Implement: `register()`, `get()`, `list_active()`, `unregister()`
- [ ] Auto-discover and register agents on app startup
- [ ] Add Redis caching for agent lookups

## Task 3: Agent Schemas
- [ ] Create `apps/api/app/schemas/__init__.py`
- [ ] Create `apps/api/app/schemas/agent.py`:
  - `AgentCreate`, `AgentUpdate`, `AgentResponse`, `AgentListResponse`
- [ ] Create `apps/api/app/schemas/gateway.py`:
  - `GatewayExecuteRequest`, `GatewayExecuteResponse`

## Task 4: Agent CRUD Endpoints
- [ ] Create `apps/api/app/api/v1/agents.py`
- [ ] `POST /api/v1/agents` — create agent (admin)
- [ ] `GET /api/v1/agents` — list active agents (public, with category filter)
- [ ] `GET /api/v1/agents/{slug}` — get agent by slug (public)
- [ ] `PUT /api/v1/agents/{id}` — update agent (admin)
- [ ] `DELETE /api/v1/agents/{id}` — soft-delete agent (admin)
- [ ] Register route in v1 router

## Task 5: API Gateway — Execute Endpoint
- [ ] Create `apps/api/app/api/v1/gateway.py`
- [ ] `POST /api/v1/agents/{slug}/execute` endpoint
- [ ] Implement execution flow: validate → lookup → execute → record → respond
- [ ] Handle errors: agent not found, agent inactive, validation failed, execution error
- [ ] Return standardized response with latency_ms

## Task 6: Agent Documentation Endpoint
- [ ] `GET /api/v1/agents/{slug}/docs` — returns auto-generated documentation
- [ ] Include: input schema, output schema, examples, pricing, rate limits

## Task 7: Usage Event Recording
- [ ] Create `apps/api/app/services/usage.py`
- [ ] `record_usage_event()` function
- [ ] Records: agent_id, user_id, api_key_id, request_id, status, latency, cost
- [ ] Async — does not block response

## Task 8: Example Agent (Hello World)
- [ ] Create `agents/hello/__init__.py`
- [ ] Create `agents/hello/agent.py` — simple echo/hello agent for testing
- [ ] Register in agent registry
- [ ] Verify it works through gateway endpoint

## Task 9: Agent Database Migration
- [ ] Create Alembic migration for `agents` table enhancements
- [ ] Add `input_schema_json`, `output_schema_json` columns
- [ ] Seed database with example agent record

## Task 10: Frontend — Agent Catalog
- [ ] Create `apps/web/src/pages/Agents.tsx` — full implementation
- [ ] List agents with: name, category, description, price
- [ ] Filter by category
- [ ] Click agent → detail page with documentation
- [ ] Create `apps/web/src/pages/AgentDetail.tsx`

## Task 11: Tests
- [ ] Test agent CRUD endpoints
- [ ] Test gateway execution (success + error cases)
- [ ] Test agent registry (register, get, list)
- [ ] Test usage recording
- [ ] Test input validation

## Definition of Done
- [ ] Can register agent via API and code
- [ ] Agent appears in public catalog
- [ ] Can execute agent through gateway
- [ ] Input validation rejects bad input
- [ ] Usage event recorded on execution
- [ ] Agent docs auto-generated
- [ ] Frontend shows catalog
- [ ] All tests pass
