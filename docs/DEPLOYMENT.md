# AgentHub — Railway Deployment Guide

## Prerequisites
- Railway account (https://railway.app)
- GitHub repo connected (https://github.com/Harsha6215/agent-hub)

## Step 1: Create Railway Project

1. Go to Railway → "New Project" → "Deploy from GitHub repo"
2. Select `Harsha6215/agent-hub`
3. Railway auto-detects the Dockerfile

## Step 2: Add PostgreSQL

1. In your Railway project → "Add Service" → "PostgreSQL"
2. Copy the `DATABASE_URL` from the PostgreSQL service variables
3. Replace `postgresql://` with `postgresql+asyncpg://` for the backend

## Step 3: Add Redis

1. "Add Service" → "Redis"
2. Copy `REDIS_URL` from Redis service variables

## Step 4: Configure Backend Service

Set these environment variables on the backend service:

```
APP_ENV=production
APP_VERSION=0.1.0
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(64))">
DATABASE_URL=postgresql+asyncpg://<from-railway-postgres>
REDIS_URL=<from-railway-redis>
CORS_ORIGINS=https://your-domain.com
LOG_LEVEL=INFO
LOG_JSON=true
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**CRITICAL:** Generate a real SECRET_KEY. Never use the default.

## Step 5: Backend Dockerfile

Railway should use `docker/backend.Dockerfile` with context at repo root.

Build command: `docker build -f docker/backend.Dockerfile .`
Start command: (uses ENTRYPOINT from Dockerfile)

Or for Railway nixpacks, set:
- Root directory: `.`
- Build command: `pip install -r apps/api/requirements.txt`
- Start command: `uvicorn apps.api.app.main:app --host 0.0.0.0 --port $PORT`

## Step 6: Frontend (Optional for Beta)

For the beta, serve frontend from the same backend or deploy separately.

Option A: Serve static build from backend (simplest)
Option B: Deploy frontend separately to Vercel/Netlify

## Step 7: Custom Domain

1. Railway → Backend service → Settings → "Custom Domain"
2. Add your domain (e.g., `api.agenthub.dev`)
3. Configure DNS (CNAME to Railway)
4. HTTPS is automatic

## Step 8: Verify Production

Run these checks after deployment:

```bash
# Health
curl https://your-domain.com/health

# OpenAPI
curl https://your-domain.com/openapi.json | jq .info

# MCP Tools
curl https://your-domain.com/mcp/tools | jq .count

# llms.txt
curl https://your-domain.com/llms.txt

# Register
curl -X POST https://your-domain.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"yourpassword"}'

# Create API key (use token from register response)
curl -X POST https://your-domain.com/api/v1/keys \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Production Key"}'

# Execute agent (use API key from key creation)
curl -X POST https://your-domain.com/api/v1/agents/gst-calculator/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_live_..." \
  -d '{"input":{"operation":"calculate_gst","amount":"1000","gst_rate":"18"}}'

# MCP Execute
curl -X POST https://your-domain.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"gst-calculator","arguments":{"operation":"calculate_gst","amount":"5000","gst_rate":"18"}}}'
```

## Step 9: Production Checklist

### Security
- [ ] SECRET_KEY is strong (64+ random chars)
- [ ] APP_ENV=production
- [ ] CORS restricted to actual domain
- [ ] No secrets in GitHub
- [ ] Debug mode off
- [ ] Rate limits active (100/day free)
- [ ] API key hashing (HMAC-SHA256)
- [ ] JWT validation (iss + aud)

### Functionality
- [ ] /health → 200
- [ ] /mcp/tools → lists 4 agents
- [ ] Register → returns tokens
- [ ] API key creation → shows key once
- [ ] GST Calculator → correct math
- [ ] Business Calculator → correct math
- [ ] EMI Calculator → correct math
- [ ] Usage recording works
- [ ] Rate limiting returns 429 when exceeded

### Monitoring
- [ ] Railway logs accessible
- [ ] Structured JSON logging enabled
- [ ] Health check configured in Railway

## Step 10: Record Baseline

Before sharing with anyone:
```
Registered users: 0
API keys: 0
External calls: 0
Repeat users: 0
```

Then invite first 5-10 developers and track daily.
