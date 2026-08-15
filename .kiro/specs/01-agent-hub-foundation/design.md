# Epic 1 — Agent Hub Foundation: Design

## Architecture Overview

```
agent-hub/
│
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── app/
│   │   │   ├── core/          # Config, database, logging, security
│   │   │   ├── api/v1/        # API routes
│   │   │   ├── models/        # SQLAlchemy ORM models
│   │   │   ├── schemas/       # Pydantic request/response schemas
│   │   │   ├── services/      # Business logic
│   │   │   ├── middleware/    # Request ID, logging, rate limit
│   │   │   └── main.py       # App entry point
│   │   ├── tests/
│   │   ├── alembic/
│   │   ├── requirements.txt
│   │   └── alembic.ini
│   │
│   └── web/                    # React frontend
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   ├── lib/
│       │   ├── styles/
│       │   ├── App.tsx
│       │   └── main.tsx
│       ├── package.json
│       ├── vite.config.ts
│       └── tailwind.config.js
│
├── agents/                     # Agent implementations (Epic 5+)
│   └── README.md
│
├── packages/
│   └── shared/                 # Shared types/constants
│
├── docker/
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── ROADMAP.md
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

## Technology Decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Backend | FastAPI + Python 3.11 | Async, fast, OpenAPI auto-gen, matches existing skills |
| Frontend | React 18 + Vite + TypeScript | Fast DX, lazy loading, matches existing projects |
| Database | PostgreSQL 15 | Robust, JSONB for flexible agent configs |
| Cache | Redis 7 | Rate limiting, caching, session store |
| ORM | SQLAlchemy 2.0 (async) | Mature, Alembic migrations, async support |
| Config | Pydantic Settings | Type-safe, .env loading, validation |
| Logging | structlog | Structured JSON, request correlation |
| Styling | Tailwind CSS 3 | Utility-first, fast prototyping |
| CI/CD | GitHub Actions | Free for public repos, good ecosystem |

## Database Schema (Initial)

### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',  -- user, admin, developer
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

### agents
```sql
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    category VARCHAR(50),
    version VARCHAR(20) DEFAULT '1.0',
    status VARCHAR(20) DEFAULT 'draft',  -- draft, active, paused, deprecated
    endpoint VARCHAR(255),
    pricing_model VARCHAR(20) DEFAULT 'per_request',
    price_per_request DECIMAL(10,4) DEFAULT 0.10,
    rate_limit_per_minute INTEGER DEFAULT 60,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

### api_keys
```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    key_hash VARCHAR(255) NOT NULL,  -- never store raw key
    key_prefix VARCHAR(10) NOT NULL, -- for identification: sk_live_xxx
    environment VARCHAR(20) DEFAULT 'development',  -- development, production
    permissions JSONB DEFAULT '["agent:execute", "usage:read"]',
    is_active BOOLEAN DEFAULT true,
    last_used_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

### usage_events
```sql
CREATE TABLE usage_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    api_key_id UUID REFERENCES api_keys(id),
    agent_id UUID REFERENCES agents(id),
    agent_version VARCHAR(20),
    request_id VARCHAR(36),
    status VARCHAR(20),  -- success, error, rate_limited
    latency_ms INTEGER,
    billable_units INTEGER DEFAULT 1,
    estimated_cost DECIMAL(10,4),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_usage_events_user ON usage_events(user_id, created_at);
CREATE INDEX idx_usage_events_agent ON usage_events(agent_id, created_at);
```

## API Design

### System Endpoints
```
GET  /health                    → {"status": "ok"}
GET  /api/v1/version            → {"version": "0.1.0", "env": "local"}
GET  /docs                      → OpenAPI Swagger UI
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input provided",
    "details": [...]
  },
  "request_id": "req_abc123"
}
```

### Success Response Format
```json
{
  "success": true,
  "data": { ... },
  "request_id": "req_abc123"
}
```

## Middleware Stack (order matters)
1. RequestIDMiddleware (outermost — assigns request_id)
2. AccessLogMiddleware (logs every request/response)
3. CORSMiddleware (handles CORS headers)

## Configuration Structure
```python
class Settings(BaseSettings):
    # App
    APP_ENV: str = "local"
    APP_VERSION: str = "0.1.0"
    APP_NAME: str = "Agent Hub"
    
    # Server
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://..."
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False
```

## Frontend Pages (Placeholders for Epic 1)
- `/dashboard` — Overview stats (empty state)
- `/agents` — Agent catalog (empty state)
- `/api-keys` — API key management (empty state)
- `/usage` — Usage analytics (empty state)
- `/docs` — Documentation (empty state)
- `/settings` — User settings (empty state)

## Docker Compose Services
| Service | Image | Port | Depends On |
|---------|-------|------|------------|
| postgres | postgres:15-alpine | 5432 | — |
| redis | redis:7-alpine | 6379 | — |
| backend | custom Dockerfile | 8000 | postgres, redis |
| frontend | custom Dockerfile | 3000 | backend |

## Testing Strategy
- Backend: pytest + pytest-asyncio + httpx (TestClient)
- Focus: health endpoints, config loading, DB connection
- CI: GitHub Actions runs tests on every push
