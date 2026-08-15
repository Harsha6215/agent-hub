# Epic 6 — Public Beta & Developer Experience: Design

## Architecture (unchanged)

No new backend services. Epic 6 is primarily frontend + polish of existing APIs.

```
Existing Backend (unchanged)
├── /api/v1/auth/*          — register, login, me
├── /api/v1/keys/*          — create, list, revoke
├── /api/v1/agents/*        — catalog, execute
├── /api/v1/usage/*         — summary, daily, by-agent
├── /mcp/*                  — MCP protocol
├── /llms.txt               — AI discovery
├── /.well-known/ai-plugin  — Plugin manifest
└── /api/v1/developers/*    — Docs, quickstart, examples

Frontend (updated)
├── / (landing page)
├── /agents (public catalog)
├── /agents/:slug (agent detail + try-it)
├── /login
├── /register
├── /dashboard (authenticated)
├── /api-keys (authenticated)
├── /usage (authenticated)
└── /docs
```

## 6.1 Landing Page Design

```
┌─────────────────────────────────────────────┐
│  Agent Hub                        [Sign Up] │
│                                             │
│  Production-ready APIs for AI agents.       │
│  Give your AI capabilities without          │
│  building every utility yourself.           │
│                                             │
│  [Get Free API Key]                         │
│                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│  │💰 Biz   │ │🧾 GST   │ │🏦 EMI   │      │
│  │Calc     │ │Calc     │ │Calc     │      │
│  │₹0.10/req│ │₹0.10/req│ │₹0.15/req│      │
│  └─────────┘ └─────────┘ └─────────┘      │
│                                             │
│  Works with: REST • MCP • OpenAPI          │
│                                             │
│  curl -X POST .../agents/gst/execute       │
│  -H "X-API-Key: sk_live_..."              │
│  -d '{"input":{"operation":"calculate_gst", │
│       "amount":"1000","gst_rate":"18"}}'    │
│                                             │
└─────────────────────────────────────────────┘
```

## 6.2 Agent Detail Page

Each agent gets:
- Name, description, category, version, price
- Operations list with descriptions
- Try-it form (input → submit → see response)
- Code examples: curl, Python, JavaScript
- MCP tool definition
- Rate limit info

## 6.3 Self-Service Flow

```
Landing → "Get API Key" → Register form → Auto-create first key → Show key (once) → Redirect to dashboard
```

Key UX decision: minimize steps between "interested" and "first API call."

## 6.4 Usage Dashboard (existing API, new frontend)

Uses existing endpoints:
- `GET /api/v1/usage` — monthly summary
- `GET /api/v1/usage/daily` — daily breakdown
- `GET /api/v1/usage/by-agent` — per-agent breakdown

Frontend renders these as cards + simple bar chart.

## 6.5 Quota Display

Frontend addition to dashboard:
```
Your Plan: Free
Daily Limit: 100 requests
Used Today: 43
Remaining: 57
```

Rate limit info available from existing rate limiter — just needs to be exposed in a lightweight endpoint or calculated client-side.

## 6.6 Beta Analytics (backend)

New lightweight endpoint (admin only):
```
GET /api/v1/admin/beta-metrics
→ {
    registered_users: 25,
    api_keys_created: 20,
    total_external_calls: 142,
    daily_active_users: 3,
    most_used_agent: "gst-calculator",
    repeat_users: 5,
  }
```

Uses existing models — just new queries against users, api_keys, usage_events tables.

## What NOT to Build

- No payment page
- No subscription selector
- No Stripe/Razorpay integration
- No "Pro" plan activation
- No agent marketplace
- No user-generated agents
- No complex analytics dashboards

## Deployment Plan

Single-instance deployment:
- Railway (or Render / Fly.io)
- PostgreSQL managed instance
- Redis managed instance
- Custom domain: agenthub.dev (or similar)
- HTTPS enforced
- Production SECRET_KEY set
- APP_ENV=production

## Files to Create/Modify

### Frontend (primary work)
- `apps/web/src/pages/Landing.tsx` — new landing page
- `apps/web/src/pages/AgentDetail.tsx` — enhanced with try-it form
- `apps/web/src/pages/Agents.tsx` — public catalog (no auth required)
- `apps/web/src/pages/Dashboard.tsx` — usage + quota display
- `apps/web/src/App.tsx` — landing route, public vs protected routes

### Backend (minimal)
- `apps/api/app/api/v1/admin.py` — add beta-metrics endpoint
- Possibly a `/api/v1/quota` endpoint for current user's remaining quota

### Documentation
- `README.md` — update with public URL
- `docs/DEPLOYMENT.md` — Railway deployment guide
