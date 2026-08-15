# Epic 3 — Authentication + Usage Metering: Tasks

## Task 1: Security Utilities
- [ ] Create `apps/api/app/core/security.py`
  - Password hashing (passlib bcrypt)
  - JWT creation (access + refresh tokens)
  - JWT verification and decoding
  - API key generation (sk_live_ / sk_dev_ + 32 chars)
  - API key hashing (SHA-256 + salt)

## Task 2: Auth Schemas
- [ ] Create `apps/api/app/schemas/auth.py`
  - `RegisterRequest` (email, password, name)
  - `LoginRequest` (email, password)
  - `TokenResponse` (access_token, refresh_token, token_type, expires_in)
  - `UserResponse` (id, email, name, role, tier, created_at)

## Task 3: Auth Service
- [ ] Create `apps/api/app/services/auth.py`
  - `register_user()` — create user, hash password, return tokens
  - `login_user()` — verify credentials, return tokens
  - `refresh_tokens()` — verify refresh, issue new pair
  - `logout_user()` — revoke refresh token
  - Brute force protection (track failed attempts in Redis)

## Task 4: Auth Endpoints
- [ ] Create `apps/api/app/api/v1/auth.py`
  - `POST /api/v1/auth/register`
  - `POST /api/v1/auth/login`
  - `POST /api/v1/auth/refresh`
  - `POST /api/v1/auth/logout`
  - `GET /api/v1/auth/me`
- [ ] Register in v1 router

## Task 5: Auth Dependencies
- [ ] Create `apps/api/app/core/deps.py`
  - `get_current_user()` — decode JWT, return user
  - `get_current_admin()` — verify admin role
  - `validate_api_key()` — validate API key from header, return user + key

## Task 6: API Key Schemas & Service
- [ ] Create `apps/api/app/schemas/key.py`
  - `KeyCreateRequest` (name, environment)
  - `KeyCreateResponse` (id, name, full_key, prefix, created_at) — full key only here
  - `KeyListResponse` (id, name, prefix, environment, last_used_at, created_at)
- [ ] Create `apps/api/app/services/key_manager.py`
  - `create_key()` — generate, hash, store, return full key once
  - `validate_key()` — hash incoming key, compare, return user
  - `list_keys()` — return user's keys (prefix only)
  - `revoke_key()` — set is_active=false
  - `update_last_used()` — update last_used_at timestamp

## Task 7: API Key Endpoints
- [ ] Create `apps/api/app/api/v1/keys.py`
  - `POST /api/v1/keys` — create (auth required)
  - `GET /api/v1/keys` — list user's keys (auth required)
  - `DELETE /api/v1/keys/{id}` — revoke (auth required)
  - `PUT /api/v1/keys/{id}` — rename (auth required)
- [ ] Register in v1 router

## Task 8: Rate Limiter
- [ ] Create `apps/api/app/services/rate_limiter.py`
  - Redis sliding window implementation
  - `check_rate_limit(user_id, tier)` → allowed, remaining, reset
  - Rate limit tiers: free=100/day, developer=1000/day, pro=10000/day
- [ ] Add rate limit check to gateway execution flow
- [ ] Return 429 with `Retry-After` header when exceeded
- [ ] Add rate limit headers to all gateway responses

## Task 9: Usage Writer
- [ ] Create `apps/api/app/services/usage_writer.py`
  - `record_usage_event()` — async background task
  - Calculates estimated_cost based on agent pricing
  - Non-blocking (fire-and-forget with error logging)

## Task 10: Usage Endpoints
- [ ] Create `apps/api/app/schemas/usage.py`
  - `UsageSummaryResponse`, `DailyUsageResponse`, `AgentUsageResponse`
- [ ] Create `apps/api/app/api/v1/usage.py`
  - `GET /api/v1/usage` — total usage current month
  - `GET /api/v1/usage/daily` — daily breakdown
  - `GET /api/v1/usage/by-agent` — grouped by agent
  - `GET /api/v1/usage/summary` — estimated cost summary
- [ ] Register in v1 router

## Task 11: Admin Analytics Endpoints
- [ ] Create `apps/api/app/api/v1/admin.py`
  - `GET /api/v1/admin/analytics/overview` — total users, calls, revenue
  - `GET /api/v1/admin/analytics/agents` — top agents by usage
  - `GET /api/v1/admin/analytics/revenue` — estimated revenue per agent
- [ ] Require admin role

## Task 12: Database Migration
- [ ] Alembic migration: add `tier`, `daily_limit` to users
- [ ] Alembic migration: create `refresh_tokens` table
- [ ] Seed admin user

## Task 13: Integrate Auth into Gateway
- [ ] Update gateway execute endpoint to require API key auth
- [ ] Check rate limit before execution
- [ ] Record usage with user_id and api_key_id
- [ ] Add rate limit headers to response

## Task 14: Frontend — Login & Register Pages
- [ ] Create `apps/web/src/pages/Login.tsx` — email + password form
- [ ] Create `apps/web/src/pages/Register.tsx` — registration form
- [ ] Create `apps/web/src/lib/auth.ts` — AuthContext, token management
- [ ] Create `apps/web/src/components/auth/ProtectedRoute.tsx`
- [ ] Update App.tsx with auth routes and protection

## Task 15: Frontend — API Keys Page
- [ ] Full implementation of `apps/web/src/pages/ApiKeys.tsx`
  - Create key button → shows full key in modal (copy button)
  - Table: name, prefix, environment, last used, created
  - Delete button with confirmation

## Task 16: Frontend — Usage Page
- [ ] Full implementation of `apps/web/src/pages/Usage.tsx`
  - Total requests this month (big number)
  - Daily requests line chart (Recharts)
  - By-agent breakdown bar chart
  - Estimated cost display

## Task 17: Tests
- [ ] Test registration flow (success + duplicate email)
- [ ] Test login flow (success + wrong password)
- [ ] Test JWT validation (valid + expired + invalid)
- [ ] Test API key creation and validation
- [ ] Test rate limiting (allow + deny)
- [ ] Test usage recording
- [ ] Test usage aggregation endpoints
- [ ] Test admin endpoints (admin + non-admin)

## Definition of Done
- [ ] Full auth flow works (register → login → call agent → see usage)
- [ ] API keys can be created, used, and revoked
- [ ] Rate limiting works correctly per tier
- [ ] Usage is tracked and visible in dashboard
- [ ] Admin can see analytics
- [ ] Frontend has login, keys, and usage pages
- [ ] All tests pass
- [ ] No secrets stored in plain text
