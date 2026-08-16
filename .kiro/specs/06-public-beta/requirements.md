# Epic 6 — Public Beta & Developer Experience: Requirements

## Objective
Put AgentHub in front of real users/AI agents and measure actual demand. The goal is NOT more agents — it's validating that the existing 3 agents attract usage.

## Success Metrics (ordered by priority)
1. 25 registered users
2. 20 API keys created
3. 100 external API calls (not our own tests)
4. 5 repeat users (>1 day with calls)
5. 3 daily active users
6. **Time to First Successful API Call < 5 minutes** (measured)
7. 1 person asking "how do I pay for more?"

## What We're Testing
- Can a developer go from "what is this?" to "I called an agent" in under 5 minutes?
- Do AI agents/developers actually want these utilities via API?
- Which agent gets the most usage?
- Do people come back?

## Guardrails (APPROVED)

### G1: No polished SaaS dashboard before usable API experience
Focus on: landing page → try-it → API key → first call. NOT admin panels.

### G2: Try-in-Browser is required
Every agent detail page must have a working form:
- Select operation
- Fill inputs
- Click "Calculate"
- See result immediately
- Then show "API equivalent" curl/code below

### G3: Measure time-to-first-call
Track timestamp between registration and first successful API call.
This is a product quality metric, not just a target.

### G4: Abuse protection before public launch
- Rate limit signup endpoint (max 5 registrations per IP per hour)
- Request body size limits
- CORS restricted to actual domain
- No secrets in git
- Debug mode disabled in production
- API keys can be revoked
- Auth errors don't leak info

### G5: Feedback mechanism
Simple per-agent feedback:
- 👍 / 👎 buttons after trying an agent
- Optional text feedback field
- Stored for product decisions

## Phases

### 6.1 Developer Experience
- Landing page that explains AgentHub in 10 seconds
- Agent catalog with live try-it forms
- Copy-paste code snippets (curl, Python, JS)
- MCP setup instructions
- Time-to-first-call < 5 minutes

### 6.2 Public Agent Catalog
- Each agent has a dedicated page: description, operations, pricing, examples
- **Try-in-Browser form** (input → calculate → result → show API equivalent)
- Filter by category
- Public — no login required to browse

### 6.3 API Key Self-Service
- Register → auto-create first key → copy → call API
- Key shown once, hash stored
- No manual intervention needed
- Key management: create, list, revoke

### 6.4 Usage Dashboard
- Requests today / this month
- Breakdown by agent
- Estimated cost (in ₹) — record hypothetical cost even though free
- Success/failure rate
- Quota remaining (visual progress bar)

### 6.5 Rate Limits & Quotas
- Free Beta: 100 requests/day
- Show remaining quota in dashboard
- 429 with clear messaging when exceeded
- Record hypothetical cost for future billing decisions

### 6.6 Beta Analytics (internal)
- Track: registrations, key creation, first call, repeat usage
- **Agent demand score**: unique users, total calls, repeat users, success rate, growth
- Distinguish: total requests vs external requests vs test requests
- Measure time-to-first-call per user
- Daily active users
- Feedback collected

## Explicitly Out of Scope
- ❌ Payment processing (Razorpay/Stripe)
- ❌ Subscription management
- ❌ New agents (no Salary, Investment, Job, etc.)
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
