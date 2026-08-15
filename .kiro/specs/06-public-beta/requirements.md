# Epic 6 — Public Beta & Developer Experience: Requirements

## Objective
Put AgentHub in front of real users/AI agents and measure actual demand. The goal is NOT more agents — it's validating that the existing 3 agents attract usage.

## Success Metrics (ordered by priority)
1. 25 registered users
2. 20 API keys created
3. 100 external API calls (not our own tests)
4. 5 repeat users
5. 3 daily active users
6. 1 person asking "how do I pay for more?"

## What We're Testing
- Can a developer go from "what is this?" to "I called an agent" in under 5 minutes?
- Do AI agents/developers actually want these utilities via API?
- Which agent gets the most usage?
- Do people come back?

## Phases

### 6.1 Developer Experience
- Landing page that explains AgentHub in 10 seconds
- Agent catalog with live try-it examples
- Copy-paste code snippets (curl, Python, JS)
- MCP setup instructions
- Time-to-first-call < 5 minutes

### 6.2 Public Agent Catalog
- Each agent has a dedicated page: description, operations, pricing, examples
- Filter by category
- Search
- Public — no login required to browse

### 6.3 API Key Self-Service
- Register → create key → copy → call API
- Key shown once, hash stored
- No manual intervention needed
- Key management: create, list, revoke

### 6.4 Usage Dashboard
- Requests today / this month
- Breakdown by agent
- Estimated cost (in ₹)
- Success/failure rate

### 6.5 Rate Limits & Quotas
- Free: 100 requests/day
- Beta: 1,000 requests/day (manual upgrade)
- Show remaining quota in dashboard
- 429 with clear messaging when exceeded

### 6.6 Beta Analytics (internal)
- Track: registrations, key creation, first call, repeat usage
- Identify most/least used agents
- Measure time-to-first-call
- Daily active users

## Explicitly Out of Scope
- ❌ Payment processing (Razorpay/Stripe)
- ❌ Subscription management
- ❌ New agents
- ❌ Marketplace / third-party agents
- ❌ Mobile app
- ❌ Enterprise features
- ❌ Complex billing engine
- ❌ Kubernetes / infrastructure scaling

## Technical Constraints
- Use existing auth (JWT + API keys)
- Use existing rate limiter
- Use existing usage recording
- Frontend: React + Tailwind (existing stack)
- No new backend dependencies unless absolutely necessary
- Deploy on Railway or similar single-instance platform
