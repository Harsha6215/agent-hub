# Epic 6 — Public Beta & Developer Experience: Tasks

## Phase 6.1: Landing Page & Developer Experience

### Task 1: Landing Page
- [ ] Create `apps/web/src/pages/Landing.tsx`
- [ ] Hero: "Production-ready APIs for AI agents" + CTA
- [ ] Agent cards (3 agents with name, price, category)
- [ ] Live code example (curl with copy button)
- [ ] "Works with: REST • MCP • OpenAPI" section
- [ ] Link to docs, GitHub, sign up
- [ ] Route as `/` (unauthenticated)

### Task 2: Public Agent Catalog (no login required)
- [ ] Make `/agents` accessible without auth
- [ ] Each agent card links to detail page
- [ ] Filter by category
- [ ] Show: name, description, price, operations count

### Task 3: Agent Detail Page (enhanced)
- [ ] Try-it form: select operation, fill fields, submit, see response
- [ ] Code examples panel: curl, Python, JavaScript (copy buttons)
- [ ] MCP tool definition display
- [ ] Pricing and rate limit info
- [ ] "Get API Key" CTA if not logged in

### Task 4: Streamlined Onboarding
- [ ] Register page creates first API key automatically
- [ ] After registration: show key in modal with copy button + "Key shown once" warning
- [ ] Redirect to dashboard after dismissing
- [ ] Time-to-first-call target: < 5 minutes

---

## Phase 6.2: Dashboard & Usage

### Task 5: Dashboard Page (authenticated)
- [ ] Today's requests (big number)
- [ ] Monthly total
- [ ] Estimated cost (₹)
- [ ] Success rate
- [ ] Quota remaining (daily)
- [ ] Quick links: create key, view agents, docs

### Task 6: Usage Breakdown
- [ ] Daily bar chart (last 30 days)
- [ ] By-agent breakdown with percentages
- [ ] Most-used agent highlighted

### Task 7: Quota Display
- [ ] Show plan name (Free/Beta)
- [ ] Daily limit vs used today
- [ ] Visual progress bar
- [ ] "Upgrade" link (points to contact/waitlist for now)

---

## Phase 6.3: Beta Analytics (admin)

### Task 8: Beta Metrics Endpoint
- [ ] `GET /api/v1/admin/beta-metrics` (admin only)
- [ ] Returns: registered_users, api_keys_created, total_calls, daily_active_users, most_used_agent, repeat_users, calls_last_24h, calls_last_7d
- [ ] Simple queries against existing tables

### Task 9: Analytics Tracking
- [ ] Track first_call timestamp per user (via usage_events)
- [ ] Identify repeat users (>1 day with calls)
- [ ] External calls filter (exclude known test/dev API keys)

---

## Phase 6.4: Documentation & Polish

### Task 10: README Update
- [ ] Public URL (once deployed)
- [ ] Quick start in 3 steps
- [ ] Agent list with pricing
- [ ] MCP setup snippet
- [ ] Link to live docs

### Task 11: Deployment Guide
- [ ] Create `docs/DEPLOYMENT.md`
- [ ] Railway deployment steps
- [ ] Environment variables checklist
- [ ] Database setup
- [ ] Redis setup
- [ ] Domain + HTTPS
- [ ] Health check verification

---

## Phase 6.5: Pre-Launch Checklist

### Task 12: Production Readiness
- [ ] Generate strong SECRET_KEY
- [ ] Set APP_ENV=production
- [ ] Configure production DATABASE_URL
- [ ] Configure production REDIS_URL
- [ ] Restrict CORS to actual domain
- [ ] Enable LOG_JSON=true
- [ ] Verify health endpoint works
- [ ] Verify auth works
- [ ] Verify rate limiting works
- [ ] Verify all 3 agents work
- [ ] Verify MCP works
- [ ] Run full test suite green

### Task 13: Launch
- [ ] Deploy to Railway/Render
- [ ] Verify public access
- [ ] Create personal API key
- [ ] Make first external call
- [ ] Share with 5 developers for feedback
- [ ] Post to relevant communities (ProductHunt, Reddit, Twitter)
- [ ] Monitor beta-metrics daily

---

## Definition of Done
- [ ] Landing page live and attractive
- [ ] Developer can register → get key → call agent in < 5 minutes
- [ ] Agent catalog browsable without login
- [ ] Usage dashboard shows real data
- [ ] Rate limits visible to users
- [ ] Beta metrics tracking active
- [ ] Deployed to production URL
- [ ] First 10 external users registered
- [ ] No regressions (99 tests passing)
