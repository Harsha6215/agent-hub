# Epic 5 — First Revenue Agents: Requirements

## Objective
Build the first production-quality, deterministic utility agents that generate revenue. Establish the agent creation template so future agents can be added with minimal friction.

## Business Context
- Epics 1–4 were infrastructure investment
- Epic 5 is the first step toward return
- Target: 100 external API calls → 10 external users → first paying customer
- We build 3 agents then pause and measure before investing more

## Agents to Build (in order)

### 5.1 Business Calculator Agent
- Profit calculation (revenue - cost)
- Margin calculation (profit / revenue × 100)
- Markup calculation (profit / cost × 100)
- Break-even calculation (fixed costs / (price - variable cost))
- Discount calculation (original × discount% / 100)

### 5.2 GST Calculator Agent
- Forward: Calculate GST amount and total from base amount + rate
- Reverse: Extract base amount from GST-inclusive price
- Supported rates: 0%, 5%, 12%, 18%, 28%
- CGST/SGST split for intra-state
- IGST for inter-state

### 5.3 Loan/EMI Calculator Agent
- EMI calculation from principal, rate, tenure
- Total interest payable
- Total payment
- Amortization schedule (optional, first 12 months)
- Loan eligibility estimate (income-based)

## Architectural Requirements

### MCP Execution Must Go Through Gateway
```
MCP tools/call → MCP Adapter → Gateway → Auth → Rate Limit → Execute → Usage → Response
```
- MCP discovery (tools/list) remains public
- MCP execution MUST use the authenticated gateway path
- No free backdoor around paid APIs
- Usage recorded for every execution regardless of entry point

### Agent Creation Template
Adding a new agent should require ONLY:
1. Create `agents/{category}/{slug}/agent.py`
2. Implement BaseAgent (name, slug, schemas, execute)
3. Agent auto-discovers on startup
4. Everything else is automatic (MCP, REST, docs, usage, pricing)

### Pricing
- Each agent defines `price_per_request` in paisa
- Business Calculator: ₹0.10/request (10 paisa)
- GST Calculator: ₹0.10/request (10 paisa)
- EMI Calculator: ₹0.15/request (15 paisa)
- Pricing is metadata only — no payment collection yet

## Non-Requirements (explicitly excluded)
- ❌ Payment gateway / Razorpay / Stripe
- ❌ Subscriptions or billing
- ❌ Marketplace or user-generated agents
- ❌ AI/LLM orchestration
- ❌ Web crawling or scraping
- ❌ Kubernetes or microservices
- ❌ Enterprise SSO

## Success Criteria
1. Business Calculator agent works via REST and MCP
2. GST Calculator agent works via REST and MCP
3. EMI Calculator agent works via REST and MCP
4. MCP execution uses gateway (auth + rate limit + usage)
5. All agents auto-discovered at startup
6. Adding a new agent = 1 file, no other changes needed
7. Pricing metadata present on all agents
8. All existing tests pass (no regression)
9. New agent-specific tests pass
10. OpenAPI, MCP tools, llms.txt all updated automatically
