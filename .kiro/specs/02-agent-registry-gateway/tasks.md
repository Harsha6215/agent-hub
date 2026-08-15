# Epic 2 — Agent Registry + API Gateway: Tasks

## Task 1: BaseAgent Abstract Class
- [x] Create `agents/__init__.py`
- [x] Create `agents/base.py` — BaseAgent ABC with: name, slug, version, description, category
- [x] Implement abstract methods: `get_input_schema()`, `get_output_schema()`, `execute()`
- [x] Implement `get_documentation()` method (auto-generates from schemas)
- [x] Create `agents/README.md` — instructions for creating new agents

## Task 2: Agent Registry Service
- [x] Create `apps/api/app/services/__init__.py`
- [x] Create `apps/api/app/services/agent_registry.py` — AgentRegistry class
- [x] Implement: `register()`, `get()`, `list_active()`, `unregister()`
- [x] Auto-discover and register agents on app startup
- [ ] Add Redis caching for agent lookups

## Task 3: Agent Schemas
- [x] Create `apps/api/app/schemas/__init__.py`
- [x] Create `apps/api/app/schemas/agent.py`: AgentCreate, AgentUpdate, AgentResponse, AgentListResponse
- [x] Create `apps/api/app/schemas/gateway.py`: GatewayExecuteRequest, GatewayExecuteResponse

## Task 4: Agent CRUD Endpoints
- [x] Create `apps/api/app/api/v1/agents.py`
- [x] `POST /api/v1/agents` — create agent (admin)
- [x] `GET /api/v1/agents` — list active agents (public, with category filter)
- [x] `GET /api/v1/agents/{slug}` — get agent by slug (public)
- [x] `PUT /api/v1/agents/{id}` — update agent (admin)
- [x] `DELETE /api/v1/agents/{id}` — soft-delete agent (admin)
- [x] Register route in v1 router

## Task 5: API Gateway — Execute Endpoint
- [x] Create `apps/api/app/api/v1/gateway.py`
- [x] `POST /api/v1/agents/{slug}/execute` endpoint
- [x] Implement execution flow: validate → lookup → execute → record → respond
- [x] Handle errors: agent not found, agent inactive, validation failed, execution error
- [x] Return standardized response with latency_ms

## Task 6: Agent Documentation Endpoint
- [x] `GET /api/v1/agents/{slug}/docs` — returns auto-generated documentation
- [x] Include: input schema, output schema, examples, pricing, rate limits

## Task 7: Usage Event Recording
- [x] Create `apps/api/app/services/usage.py`
- [x] `record_usage_event()` function
- [x] Records: agent_slug, user_id, status, latency, cost
- [x] Async — does not block response

## Task 8: Example Agent (Hello World)
- [x] Create `agents/hello/__init__.py`
- [x] Create `agents/hello/agent.py` — simple echo/hello agent for testing
- [x] Register in agent registry
- [x] Verify it works through gateway endpoint ✅

## Task 9: Agent Database Migration
- [x] Tables auto-created on startup (create_all)
- [ ] Create Alembic migration for production
- [ ] Seed database with example agent record

## Task 10: Frontend — Agent Catalog
- [x] Create `apps/web/src/pages/Agents.tsx` — full implementation
- [x] List agents with: name, category, description, price
- [x] Filter by category
- [x] Click agent → detail page with documentation
- [x] Create `apps/web/src/pages/AgentDetail.tsx`

## Task 11: Tests
- [ ] Test agent CRUD endpoints
- [ ] Test gateway execution (success + error cases)
- [ ] Test agent registry (register, get, list)
- [ ] Test usage recording
- [ ] Test input validation

## Definition of Done
- [x] Can register agent via API and code
- [x] Agent appears in public catalog
- [x] Can execute agent through gateway ✅ (tested with hello agent)
- [x] Input validation rejects bad input
- [x] Usage event recorded on execution
- [x] Agent docs auto-generated
- [x] Frontend shows catalog
- [ ] All tests pass
