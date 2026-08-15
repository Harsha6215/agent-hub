# Epic 3 — Authentication + Usage Metering: Requirements

## Overview
Add user authentication, API key management, rate limiting, and usage metering. This is the foundation for monetization — we must track who uses what and how much.

## Business Context
- Users create accounts, generate API keys, and call agents
- Every call is metered and contributes to a usage total
- Usage dashboard shows estimated cost
- Rate limiting prevents abuse of free tier
- This epic prepares us for billing (Epic 6)

## Functional Requirements

### FR-1: User Registration & Login
```
POST /api/v1/auth/register   — email + password → user created
POST /api/v1/auth/login      — email + password → JWT access + refresh tokens
POST /api/v1/auth/refresh    — refresh token → new access token
POST /api/v1/auth/logout     — revoke refresh token
GET  /api/v1/auth/me         — get current user profile
```

### FR-2: User Roles
- `user` — default, can create API keys and call agents
- `admin` — can manage agents, view all users, access admin endpoints
- `developer` — can publish agents (future use)

### FR-3: API Key Management
```
POST   /api/v1/keys          — create API key (returns full key ONCE)
GET    /api/v1/keys          — list user's keys (prefix only, never full key)
DELETE /api/v1/keys/{id}     — revoke key
PUT    /api/v1/keys/{id}     — rename, update permissions
```

#### API Key Format
- Production: `sk_live_` + 32 random chars
- Development: `sk_dev_` + 32 random chars
- Store only hash in database
- Return full key only at creation

### FR-4: API Key Authentication for Gateway
- Header: `Authorization: Bearer sk_live_xxxxxxxx`
- Gateway validates key, identifies user, checks permissions
- Records `last_used_at` timestamp on key

### FR-5: Rate Limiting
- Redis-based sliding window rate limit
- Limits per tier:
  - Free: 100 requests/day
  - Developer: 1,000 requests/day
  - Pro: 10,000 requests/day
- When exceeded: return 429 with retry-after header
- Rate limit info in response headers:
  ```
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 87
  X-RateLimit-Reset: 1692144000
  ```

### FR-6: Usage Metering
- Every agent execution generates a `usage_event`
- Fields: user_id, api_key_id, agent_id, status, latency_ms, estimated_cost
- Usage recorded async (does not slow response)
- Aggregatable by: day, week, month; by agent; by user

### FR-7: Usage Dashboard API
```
GET /api/v1/usage                    — current user's total usage
GET /api/v1/usage/daily              — daily breakdown
GET /api/v1/usage/by-agent           — grouped by agent
GET /api/v1/usage/summary            — estimated cost summary
```

#### Example response:
```json
{
  "total_requests": 4281,
  "period": "2026-08",
  "by_agent": [
    {"agent": "gst-calculator", "requests": 1892, "estimated_cost": 189.20},
    {"agent": "emi-calculator", "requests": 1123, "estimated_cost": 56.15}
  ],
  "estimated_total": 428.10,
  "currency": "INR"
}
```

### FR-8: Admin Analytics API
```
GET /api/v1/admin/analytics/overview    — total users, active users, total calls
GET /api/v1/admin/analytics/agents      — top agents by usage
GET /api/v1/admin/analytics/revenue     — estimated revenue per agent
```

### FR-9: Frontend — API Keys Page
- Create new key (shows full key once in modal)
- List existing keys (prefix only)
- Copy key button
- Delete/revoke key
- Show last used timestamp

### FR-10: Frontend — Usage Page
- Total requests this month
- Chart: daily requests (line chart)
- Breakdown by agent (bar chart)
- Estimated cost display

### FR-11: Frontend — Login/Register Pages
- Simple email + password login
- Registration form
- JWT token stored in memory (not localStorage for security)
- Auto-redirect to dashboard after login

## Non-Functional Requirements
- Rate limit check < 5ms (Redis)
- Usage recording async, non-blocking
- API key hashing with bcrypt or SHA-256 + salt
- JWT expiry: access 30min, refresh 7 days
- Rate limiting must survive Redis restart gracefully

## Acceptance Criteria
- [ ] User can register and login
- [ ] JWT authentication works on protected endpoints
- [ ] User can create API key and receives full key once
- [ ] Gateway authenticates via API key in header
- [ ] Rate limiting works and returns 429 when exceeded
- [ ] Usage events recorded for every agent execution
- [ ] Usage dashboard shows accurate totals
- [ ] Admin can see analytics overview
- [ ] Frontend has login, API keys, and usage pages
- [ ] Tests cover auth flow, rate limiting, and usage recording
