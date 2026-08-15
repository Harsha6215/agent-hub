# Epic 4 — MCP + Developer Portal: Tasks

## Task 1: MCP Protocol — Server Implementation
- [ ] Create `apps/api/app/mcp/__init__.py`
- [ ] Create `apps/api/app/mcp/server.py` — MCP server that exposes agents as tools
- [ ] Each registered agent becomes an MCP tool with name, description, input schema
- [ ] Handle `tools/list` — returns all active agents as MCP tools
- [ ] Handle `tools/call` — routes to agent execute, returns result
- [ ] Support stdio transport for local usage
- [ ] Support SSE transport for remote usage

## Task 2: MCP Tool Schema Generation
- [ ] Auto-generate MCP tool definitions from BaseAgent metadata
- [ ] Map agent input_schema to MCP tool inputSchema
- [ ] Map agent output to MCP tool content response
- [ ] Include agent description, version, pricing in tool metadata

## Task 3: OpenAPI Spec Enhancement
- [ ] Ensure all endpoints have proper OpenAPI descriptions
- [ ] Add example request/response bodies
- [ ] Add authentication documentation in OpenAPI
- [ ] Serve OpenAPI JSON at `/openapi.json`
- [ ] Swagger UI at `/docs` (already exists)
- [ ] ReDoc at `/redoc` (already exists)

## Task 4: Developer Documentation Endpoint
- [ ] Create `GET /api/v1/developers/docs` — returns full developer guide
- [ ] Create `GET /api/v1/developers/quickstart` — getting started
- [ ] Create `GET /api/v1/developers/agents` — all agent docs combined
- [ ] Include: authentication, rate limits, error codes, SDKs

## Task 5: llms.txt / Agent Metadata
- [ ] Create `GET /.well-known/ai-plugin.json` — AI plugin manifest
- [ ] Create `GET /llms.txt` — plain text description for LLMs
- [ ] Include: what agents are available, how to call them, pricing

## Task 6: SDK Stub Generation
- [ ] Create `apps/api/app/api/v1/sdk.py` — SDK download/info endpoint
- [ ] Generate Python SDK usage example
- [ ] Generate JavaScript/TypeScript SDK usage example
- [ ] Generate cURL examples for each agent

## Task 7: Developer Portal Frontend
- [ ] Update `apps/web/src/pages/Documentation.tsx` — full docs page
- [ ] Add: Getting Started guide
- [ ] Add: Authentication section
- [ ] Add: Agent catalog with try-it forms
- [ ] Add: Code examples (Python, JS, cURL)
- [ ] Add: Rate limits and pricing table

## Task 8: MCP Configuration File
- [ ] Create example `mcp.json` for clients to use
- [ ] Document how to connect Agent Hub to Claude, Cursor, Kiro
- [ ] Add to docs/MCP_SETUP.md

## Task 9: Tests
- [ ] Test MCP tools/list response
- [ ] Test MCP tools/call routing
- [ ] Test OpenAPI spec is valid
- [ ] Test developer docs endpoints
- [ ] Test llms.txt format

## Definition of Done
- [ ] Agents discoverable via MCP protocol
- [ ] MCP clients can execute agents
- [ ] Developer docs available at /docs
- [ ] llms.txt serves agent metadata
- [ ] OpenAPI spec complete and valid
- [ ] Example MCP config working
- [ ] Documentation page functional
