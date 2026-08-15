# Epic 3 — Authentication + Usage Metering: Design

## Authentication Flow

```
Register:
  Client → POST /auth/register → Create user → Return JWT pair

Login:
  Client → POST /auth/login → Verify password → Return JWT pair

API Call:
  Client → Bearer sk_live_xxx → Validate key → Identify user → Execute

Token Refresh:
  Client → POST /auth/refresh → Verify refresh token → New access token
```

## JWT Structure
```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "role": "user",
  "exp": 1692144000,
  "iat": 1692142200,
  "type": "access"
}
```

## API Key Architecture

```
Creation:
  1. Generate: sk_live_ + secrets.token_urlsafe(32)
  2. Hash key with SHA-256 + unique salt
  3. Store: key_prefix, key_hash, salt, user_id, permissions
  4. Return full key to user (ONLY TIME)

Validation:
  1. Extract key from Authorization header
  2. Get prefix (first 8 chars)
  3. Find matching key records by prefix
  4. Hash incoming key with stored salt
  5. Compare hashes
  6. Return associated user
```

## Rate Limiting Design (Redis Sliding Window)

```python
async def check_rate_limit(user_id: str, limit: int) -> RateLimitResult:
    """
    Redis sliding window counter.
    Key: rate_limit:{user_id}:{window_start}
    """
    key = f"rate_limit:{user_id}:{current_day()}"
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, 86400)  # 24 hours

    return RateLimitResult(
        allowed=current <= limit,
        limit=limit,
        remaining=max(0, limit - current),
        reset=end_of_day_timestamp(),
    )
```

## Usage Metering Architecture

```
Request → Gateway → Agent Executes → Response
                         │
                         ▼ (async background)
                  ┌──────────────┐
                  │ Usage Writer │
                  └──────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  PostgreSQL  │
                  │ usage_events │
                  └──────────────┘
```

Usage event is written asynchronously using `asyncio.create_task()` to avoid blocking the response.

## Usage Aggregation Queries

```sql
-- Daily usage for current user this month
SELECT DATE(created_at) as day, COUNT(*) as requests, SUM(estimated_cost) as cost
FROM usage_events
WHERE user_id = $1 AND created_at >= date_trunc('month', now())
GROUP BY DATE(created_at)
ORDER BY day;

-- By agent
SELECT a.name, a.slug, COUNT(u.*) as requests, SUM(u.estimated_cost) as cost
FROM usage_events u JOIN agents a ON u.agent_id = a.id
WHERE u.user_id = $1 AND u.created_at >= date_trunc('month', now())
GROUP BY a.name, a.slug;
```

## Database Schema Additions

### Extend users table
```sql
ALTER TABLE users ADD COLUMN tier VARCHAR(20) DEFAULT 'free';
-- free, developer, pro, enterprise
ALTER TABLE users ADD COLUMN daily_limit INTEGER DEFAULT 100;
```

### Refresh tokens table
```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

## File Structure (New files in Epic 3)
```
apps/api/app/
├── api/v1/
│   ├── auth.py             # Register, login, refresh, logout, me
│   ├── keys.py             # API key CRUD
│   └── usage.py            # Usage endpoints
├── core/
│   ├── security.py         # JWT, password hashing, key hashing
│   └── deps.py             # Dependencies: get_current_user, validate_api_key
├── services/
│   ├── auth.py             # Auth business logic
│   ├── key_manager.py      # API key generation, validation
│   ├── rate_limiter.py     # Redis rate limiting
│   └── usage_writer.py     # Async usage recording
├── schemas/
│   ├── auth.py             # Login, register, token schemas
│   ├── key.py              # API key schemas
│   └── usage.py            # Usage response schemas

apps/web/src/
├── pages/
│   ├── Login.tsx           # Login form
│   ├── Register.tsx        # Registration form
│   ├── ApiKeys.tsx         # Full implementation
│   └── Usage.tsx           # Full implementation
├── lib/
│   ├── auth.ts             # Auth state, token management
│   └── api.ts              # Updated with auth headers
├── components/
│   ├── auth/
│   │   └── ProtectedRoute.tsx
│   └── usage/
│       ├── UsageChart.tsx
│       └── UsageSummary.tsx
```

## Security Considerations
- Never store raw API keys — only hash
- JWT stored in httpOnly cookie or memory (not localStorage)
- Rate limit keys tied to user_id (not just API key)
- Failed login attempts tracked (brute force protection)
- API key shown to user only once at creation
- Refresh tokens are single-use (rotation)

## Rate Limit Tiers
| Tier | Daily Limit | Rate/Minute | Price |
|------|-------------|-------------|-------|
| Free | 100 | 10 | ₹0 |
| Developer | 1,000 | 30 | ₹299/mo |
| Pro | 10,000 | 60 | ₹999/mo |
| Enterprise | 100,000 | 300 | Custom |

## Frontend State Management
- Auth state: React Context with token in memory
- On page load: try refresh token → if valid, user is logged in
- On 401: redirect to login
- API keys page: fetch on mount, create shows modal with full key
- Usage page: fetch daily/agent data, render charts with Recharts
