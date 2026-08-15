# Epic 5 — First Revenue Agents: Tasks

## Phase 5.1: Agent Framework + Business Calculator

### Task 1: Shared Executor Service
- [ ] Create `apps/api/app/services/executor.py`
- [ ] Extract execution logic from gateway.py into shared executor
- [ ] Executor handles: lookup → auth → rate limit → execute → usage → return
- [ ] Both REST and MCP use the same executor
- [ ] Returns `ExecutionResult` dataclass (success, data, error, latency_ms, agent, version)

### Task 2: MCP Through Gateway
- [ ] Update `apps/api/app/mcp/server.py` → `call_mcp_tool()` uses shared executor
- [ ] MCP tools/call now goes through auth + rate limit + usage recording
- [ ] MCP discovery (tools/list) remains public and free
- [ ] MCP accepts optional `_api_key` in arguments for authenticated calls

### Task 3: Business Calculator Agent
- [ ] Create `agents/business/agent.py`
- [ ] Implement operations: profit, margin, markup, breakeven, discount
- [ ] Define input schema with `operation` enum
- [ ] Define output schema
- [ ] Set price_per_request = 10 (₹0.10)
- [ ] Verify auto-discovery registers it on startup

### Task 4: Business Calculator Tests
- [ ] Test profit calculation (revenue=1000, cost=600 → profit=400)
- [ ] Test margin calculation (profit=400, revenue=1000 → margin=40%)
- [ ] Test markup calculation (profit=400, cost=600 → markup=66.67%)
- [ ] Test breakeven (fixed=10000, price=100, variable=60 → units=250)
- [ ] Test discount (original=1000, discount=20 → savings=200, final=800)
- [ ] Test invalid operation → error
- [ ] Test missing required fields → error
- [ ] Test zero/negative edge cases

### Task 5: Verify Integration
- [ ] Business Calculator appears in `GET /mcp/tools`
- [ ] Business Calculator works via `POST /api/v1/agents/business-calculator/execute`
- [ ] Business Calculator works via MCP `tools/call`
- [ ] Usage event recorded for execution
- [ ] Pricing metadata visible in agent docs
- [ ] llms.txt updated automatically
- [ ] All existing tests pass (no regression)

---

## Phase 5.2: GST Calculator

### Task 6: GST Calculator Agent
- [ ] Create `agents/gst/agent.py`
- [ ] Operations: calculate_gst (forward), extract_gst (reverse)
- [ ] Support rates: 0, 5, 12, 18, 28
- [ ] Calculate CGST/SGST split (intra-state)
- [ ] Calculate IGST (inter-state)
- [ ] Set price_per_request = 10

### Task 7: GST Calculator Tests
- [ ] Forward: amount=1000, rate=18 → gst=180, total=1180, cgst=90, sgst=90
- [ ] Reverse: total=1180, rate=18 → base=1000, gst=180
- [ ] IGST: amount=1000, rate=18, interstate=true → igst=180
- [ ] Zero rate: amount=1000, rate=0 → gst=0, total=1000
- [ ] 28% rate test
- [ ] Invalid rate → error
- [ ] Negative amount → error

### Task 8: GST Integration Verify
- [ ] Works via REST
- [ ] Works via MCP
- [ ] No new files needed outside agent folder (framework validation)

---

## Phase 5.3: EMI/Loan Calculator

### Task 9: EMI Calculator Agent
- [ ] Create `agents/emi/agent.py`
- [ ] Operations: calculate_emi, total_interest, loan_eligibility
- [ ] EMI formula: P × r × (1+r)^n / ((1+r)^n - 1)
- [ ] Optional: first 12 months amortization schedule
- [ ] Set price_per_request = 15

### Task 10: EMI Calculator Tests
- [ ] EMI: principal=1000000, rate=8.5, tenure=20 → EMI≈8678
- [ ] Total interest calculation
- [ ] Total payment = principal + total_interest
- [ ] Loan eligibility (income=50000 → max EMI=20000 → max loan)
- [ ] Short tenure (1 year) test
- [ ] Zero rate test
- [ ] Invalid inputs (negative principal, etc.)

### Task 11: EMI Integration Verify
- [ ] Works via REST and MCP
- [ ] No framework changes needed (validates agent template)

---

## Phase 5.4: Final Verification

### Task 12: Security & Performance
- [ ] All 3 agents require API key in production mode
- [ ] Rate limiting applies to all agents
- [ ] Usage events recorded with correct pricing
- [ ] No existing tests regressed
- [ ] All new tests pass
- [ ] Docker build succeeds
- [ ] Bandit passes

### Task 13: Documentation
- [ ] OpenAPI reflects all new agents
- [ ] MCP tools list shows all agents
- [ ] llms.txt updated with new agents
- [ ] Developer quickstart examples work
- [ ] Create `docs/EPIC_5_COMPLETION.md`

## Definition of Done
- [ ] 3 revenue agents live and tested
- [ ] MCP execution goes through gateway (no free backdoor)
- [ ] Adding agent = 1 file (framework validated by agent 2 and 3)
- [ ] Pricing metadata on all agents
- [ ] 36+ existing tests pass + new agent tests
- [ ] Ready for public beta
