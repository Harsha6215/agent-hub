# Epic 3 — Authentication + Usage Metering: Tasks

## Task 1: Security Utilities
- [x] Create `apps/api/app/core/security.py`
  - Password hashing (passlib bcrypt)
  - JWT creation (access + refresh tokens)
  - JWT verification and decoding
  - API key generation (sk_live_ / sk_test_ + 32 chars)
  - API key hashing (SHA-256)

## Task 2: Auth Schemas
- [x] Create `apps/api/app/schemas/auth.py`
  - RegisterRequest, LoginRequest, TokenResponse, UserResponse

## Task 3: Auth Service
- [x] Create `apps/api/app/services/auth.py`
  - register_user(), login_user(), refresh_tokens()
  - ✅ Tested: register + login working end-to-end
- [ ] Brute force protection (track failed attempts in Redis)

## Task 4: Auth Endpoints
- [x] Create `apps/api/app/api/v1/auth.py`
  - POST /api/v1/auth/register ✅
  - POST /api/v1/auth/login ✅
  - POST /api/v1/auth/refresh ✅
  - GET /api/v1/auth/me ✅
- [x] Register in v1 router

## Task 5: Auth Dependencies
- [x] Create `apps/api/app/core/deps.py`
  - get_current_user() ✅
  - get_current_admin() ✅
  - validate_api_key() ✅

## Task 6: API Key Schemas & Service
- [x] Create `apps/api/app/schemas/key.py`
- [x] Create `apps/api/app/services/key_manager.py`
  - create_key(), list_keys(), revoke_key()

## Task 7: API Key Endpoints
- [x] Create `apps/api/app/api/v1/keys.py`
  - POST /api/v1/keys (auth required)
  - GET /api/v1/keys (auth required)
  - DELETE /api/v1/keys/{id} (auth required)
- [x] Register in v1 router

## Task 8: Rate Limiter
- [x] Create `apps/api/app/services/rate_limiter.py`
  - Redis sliding window implementation
  - Rate limit tiers: free=100/day, developer=1000/day, pro=10000/day
- [x] Add rate limit check to gateway execution flow
- [x] Return 429 with Retry-After header when exceeded

## Task 9: Usage Writer
- [x] Usage recording implemented (fire-and-forget with own session)

## Task 10: Usage Endpoints
- [ ] Create `apps/api/app/schemas/usage.py`
- [ ] Create `apps/api/app/api/v1/usage.py`
  - GET /api/v1/usage — total usage current month
  - GET /api/v1/usage/daily — daily breakdown
  - GET /api/v1/usage/by-agent — grouped by agent

## Task 11: Admin Analytics Endpoints
- [ ] Create `apps/api/app/api/v1/admin.py`
  - GET /api/v1/admin/analytics/overview
  - GET /api/v1/admin/analytics/agents

## Task 12: Database Migration
- [x] Tables auto-created on startup (create_all)
- [ ] Generate formal Alembic migration

## Task 13: Integrate Auth into Gateway
- [x] Gateway accepts optional X-API-Key header
- [x] Rate limit checked before execution
- [x] Usage recorded with user_id when authenticated

## Task 14: Frontend — Login & Register Pages
- [ ] Create Login.tsx and Register.tsx
- [ ] Create auth context and token management
- [ ] Add protected routes

## Task 15: Frontend — API Keys Page
- [ ] Full implementation of ApiKeys.tsx

## Task 16: Frontend — Usage Page
- [ ] Full implementation of Usage.tsx

## Task 17: Tests
- [ ] Test auth flow (register, login, JWT validation)
- [ ] Test API key CRUD
- [ ] Test rate limiting
- [ ] Test admin endpoints

## Definition of Done
- [x] Full auth flow works (register → login → get user) ✅
- [x] API keys can be created and used
- [x] Rate limiting works per tier
- [ ] Usage dashboard API
- [ ] Frontend auth pages
- [ ] All tests pass
