# Production Readiness Audit — Agent Hub

**Date:** August 15, 2026  
**Auditor:** Kiro (Senior Backend Architect + AppSec)  
**Scope:** Full codebase review of Epics 1–3  

---

## Scores

| Area | Score | Notes |
|------|-------|-------|
| Architecture | 8/10 | Clean separation, good monorepo structure |
| Security | 5/10 | Functional but several hardening gaps |
| Database | 6/10 | Models correct, missing indexes and constraints |
| API Design | 7/10 | Good foundation, needs pagination |
| Docker | 6/10 | Works for dev, not production-ready |
| Testing | 5/10 | 23 tests passing, needs 3x coverage |
| **Overall Production Readiness** | **5/10** | Needs hardening gate before paid APIs |

---

## A. CRITICAL Blockers (must fix before any public access)

### 1. SECRET_KEY has insecure default
- **Severity:** CRITICAL
- **File:** `apps/api/app/core/config.py` line 27
- **Problem:** `SECRET_KEY: str = "change-me-to-a-long-random-string-in-production"` — if `.env` is missing or incomplete, the app starts with a known secret.
- **Why it matters:** Anyone can forge JWTs.
- **Fix:** Fail fast on startup if SECRET_KEY equals the default in non-local environments. Add validation:
  ```python
  @model_validator(mode="after")
  def validate_secret_key(self):
      if self.APP_ENV != "local" and "change-me" in self.SECRET_KEY:
          raise ValueError("SECRET_KEY must be set in production")
      return self
  ```
- **Blocks production:** YES

### 2. API key hashing uses plain SHA-256 (no salt)
- **Severity:** CRITICAL  
- **File:** `apps/api/app/core/security.py` line 86
- **Problem:** `hashlib.sha256(key.encode()).hexdigest()` — unsalted SHA-256 is vulnerable to rainbow table attacks if the DB is compromised.
- **Why it matters:** API keys are long-lived credentials that grant access to billable APIs. If the DB leaks, all keys are immediately usable.
- **Fix:** Use HMAC-SHA256 with the server's SECRET_KEY as the key:
  ```python
  import hmac
  def hash_api_key(key: str) -> str:
      return hmac.new(settings.SECRET_KEY.encode(), key.encode(), hashlib.sha256).hexdigest()
  ```
- **Blocks production:** YES

### 3. No JWT issuer/audience validation
- **Severity:** HIGH (borderline CRITICAL)
- **File:** `apps/api/app/core/security.py` lines 63–70
- **Problem:** `jwt.decode()` does not validate `iss` or `aud` claims. Tokens from other services using the same signing key could be accepted.
- **Fix:** Add `iss` and `aud` to token creation and validate on decode:
  ```python
  payload["iss"] = "agent-hub"
  payload["aud"] = "agent-hub-api"
  # On decode:
  jwt.decode(token, key, algorithms=[alg], audience="agent-hub-api", issuer="agent-hub")
  ```
- **Blocks production:** YES (if multi-service)

### 4. Refresh tokens are not revocable
- **Severity:** HIGH
- **File:** `apps/api/app/services/auth.py` lines 82–99
- **Problem:** Refresh tokens are stateless JWTs. There's no way to revoke them after logout or password change. A stolen refresh token is valid for 7 days.
- **Why it matters:** No logout functionality actually works. "Logout" in the frontend just removes the local token.
- **Fix:** Store refresh token JTI in Redis with TTL. Check against Redis on refresh. Add a `POST /auth/logout` that blacklists the refresh token.
- **Blocks production:** YES

---

## B. HIGH Priority Fixes

### 5. Missing database indexes on usage_events
- **Severity:** HIGH
- **File:** `apps/api/app/models/usage_event.py`
- **Problem:** `user_id` column has no index. The usage endpoints (`GET /usage`, `/usage/daily`, `/usage/by-agent`) all filter by `user_id + created_at`. Without indexes, these queries will table-scan as data grows.
- **Fix:** Add:
  ```python
  from sqlalchemy import Index
  __table_args__ = (
      Index("ix_usage_user_created", "user_id", "created_at"),
      Index("ix_usage_agent_created", "agent_slug", "created_at"),
  )
  ```
- **Blocks production:** No, but will cause performance issues at ~10K rows.

### 6. Rate limiter has race condition
- **Severity:** HIGH
- **File:** `apps/api/app/services/rate_limiter.py` lines 41–55
- **Problem:** `GET` + `INCR` is not atomic. Two concurrent requests could both read count=99 (limit=100), both pass, both increment to 101.
- **Fix:** Use a Lua script or Redis `INCR` first, then check:
  ```python
  count = await redis.incr(key)
  if count == 1:
      await redis.expire(key, 86400)
  if count > limit:
      return False, 0, await redis.ttl(key)
  ```
- **Blocks production:** No, but billing accuracy is affected.

### 7. Gateway allows unauthenticated access
- **Severity:** HIGH
- **File:** `apps/api/app/api/v1/gateway.py` line 64
- **Problem:** `x_api_key: str | None = Header(None)` — the execute endpoint is callable without any authentication. Anonymous users get the "free" tier rate limit but cannot be billed.
- **Why it matters:** Before billing, all execution must be tied to a user.
- **Fix:** Before Epic 5 (revenue agents), make API key required. Keep it optional only during development.
- **Blocks production:** YES for paid agents.

### 8. No password policy enforcement beyond min length
- **Severity:** HIGH
- **File:** `apps/api/app/schemas/auth.py` line 13
- **Problem:** Only `min_length=8` is enforced. No check for common passwords, no complexity requirements.
- **Fix:** Add a check against common passwords list (top 10K), or at minimum add `max_length=72` (bcrypt limit).
- **Blocks production:** No, but increases credential stuffing risk.

### 9. Docker runs as root
- **Severity:** HIGH
- **File:** `docker/backend.Dockerfile`
- **Problem:** No `USER` directive. Container processes run as root.
- **Fix:** Add:
  ```dockerfile
  RUN useradd -m appuser
  USER appuser
  ```
- **Blocks production:** YES for any cloud deployment.

### 10. Email enumeration via registration
- **Severity:** MEDIUM (HIGH for B2B)
- **File:** `apps/api/app/services/auth.py` line 35
- **Problem:** `raise ValidationError("A user with this email already exists")` — this reveals whether an email is registered.
- **Fix:** Return the same success response regardless. Send a "you already have an account" email instead.
- **Blocks production:** No.

---

## C. MEDIUM/LOW Improvements

### 11. No `key_prefix` size validation
- **Severity:** MEDIUM
- **File:** `apps/api/app/models/api_key.py` line 21
- **Problem:** `key_prefix` is `String(10)` but the actual prefix assigned is 12 chars (`"sk_live_abc1"`). Will truncate or error.
- **Fix:** Change to `String(16)`.

### 12. `cost_paisa` stored at execution time
- **Severity:** MEDIUM (architecture)
- **File:** `apps/api/app/api/v1/gateway.py` line 103
- **Problem:** `cost_paisa=agent.price_per_request` is baked in at execution. If pricing changes, historical usage reflects old prices — which is actually correct for billing, but the field name suggests it's the cost charged, not the price at time of execution.
- **Fix:** Rename to `price_at_execution_paisa` or add a separate billing layer (as ChatGPT suggested).

### 13. No API pagination
- **Severity:** MEDIUM
- **File:** `apps/api/app/api/v1/agents.py` (list endpoint)
- **Problem:** Returns all agents without limit/offset.
- **Fix:** Add `limit: int = Query(20, le=100)` and `offset: int = Query(0, ge=0)` to list endpoints.

### 14. Login doesn't use constant-time comparison
- **Severity:** LOW
- **Confirmed safe:** passlib's `verify()` already uses constant-time comparison internally. No action needed.

### 15. CORS allows all methods and headers
- **Severity:** LOW (dev only)
- **File:** `apps/api/app/main.py`
- **Problem:** `allow_methods=["*"], allow_headers=["*"]`
- **Fix:** Restrict to actual methods used in production.

---

## D. Tests That Must Be Added

### Security Tests (CRITICAL)
1. Invalid JWT → 401
2. Expired JWT → 401
3. Refresh token used as access token → 401
4. Revoked API key → 401
5. Wrong API key → 401
6. Missing auth on protected endpoint → 401/422

### Authorization Tests (HIGH)
7. User A cannot access User B's API keys
8. User A cannot access User B's usage
9. Non-admin cannot hit admin endpoints → 403
10. Inactive user cannot authenticate → 401

### Rate Limiting Tests (HIGH)
11. Requests within limit → 200
12. Requests exceeding limit → 429 with Retry-After
13. Different tiers have different limits

### Edge Cases (MEDIUM)
14. Duplicate email registration → 422
15. Login with wrong password → 401 (generic message)
16. Empty body to gateway → 422
17. Non-existent agent → 404
18. Agent with invalid input → 422

---

## E. Production Deployment Checklist

- [ ] Generate strong SECRET_KEY (64+ random chars)
- [ ] Set APP_ENV=production
- [ ] Remove default passwords from docker-compose
- [ ] Add non-root USER to Dockerfiles
- [ ] Enable LOG_JSON=true for structured log aggregation
- [ ] Restrict CORS to actual frontend domain
- [ ] Add HTTPS/TLS (reverse proxy: nginx/caddy/traefik)
- [ ] Add database connection pooling (PgBouncer or increase pool)
- [ ] Run Alembic migrations (not create_all)
- [ ] Add health check dependencies (verify DB + Redis connectivity)
- [ ] Set up monitoring (Prometheus metrics endpoint)
- [ ] Add rate-limit headers to responses (X-RateLimit-*)
- [ ] Make API key required for gateway execute
- [ ] Add request size limits (body, headers)
- [ ] Enable pip-audit / safety in CI
- [ ] Add bandit security scan to CI
- [ ] Pin all Docker base image versions to SHA

---

## F. Recommended Remediation Order

**Do these before Epic 4:**

1. ⏱️ 15min — Fix SECRET_KEY validation (startup fail-safe)
2. ⏱️ 15min — Fix API key hashing (HMAC-SHA256)
3. ⏱️ 30min — Fix rate limiter race condition (atomic INCR)
4. ⏱️ 30min — Add composite indexes to usage_events
5. ⏱️ 15min — Fix key_prefix column size
6. ⏱️ 45min — Add refresh token revocation (Redis blacklist)
7. ⏱️ 30min — Add JWT iss/aud claims
8. ⏱️ 20min — Add pagination to list endpoints
9. ⏱️ 15min — Add non-root user to Dockerfiles
10. ⏱️ 2hr — Add security + auth test suite (items D.1–D.10)
11. ⏱️ 30min — Add bandit + pip-audit to CI

**Total estimated:** ~5–6 hours of focused work.

---

## Issues That Cannot Be Verified Without Runtime

- Actual bcrypt rounds (configured as 12, but passlib may override)
- Redis connection pool behaviour under load
- Database migration state (currently using create_all, not Alembic)
- Frontend XSS protection (token storage in localStorage is acceptable for SPAs but not ideal)
- Actual secret key strength in deployed .env

---

## Recommendations for Future Scale (NOT blockers)

- Move from `on_event` to FastAPI lifespan context manager (deprecation warning)
- Add OpenTelemetry tracing for request correlation
- Implement idempotency keys for gateway execute (before billing)
- Separate usage recording from billing (as ChatGPT recommended)
- Add agent versioning (`/agents/gst-calculator/v1/execute`)
- Structure agents/ by category (`agents/finance/gst/`, `agents/career/jobs/`)
- Consider moving from localStorage to httpOnly cookies for tokens
