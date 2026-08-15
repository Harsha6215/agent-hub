# Epic 1 — Agent Hub Foundation: Requirements

## Overview
Create the production-ready skeleton of the Agent Hub platform — an AI Agent Utility Platform that hosts revenue-generating API agents accessible to both humans and AI agents.

## Business Context
- Platform for hosting micro-SaaS API tools that AI agents can discover and invoke
- Revenue model: per-API-call pricing (₹0.05–₹5 per request)
- Target: first ₹1 of real revenue within 5 weeks
- Must be lean, deployable, and extensible

## Functional Requirements

### FR-1: Repository & Project Structure
- Monorepo structure with `apps/api` (FastAPI backend), `apps/web` (React frontend)
- Shared packages in `packages/`
- Agent implementations in `agents/`
- Docker infrastructure in `docker/`
- Documentation in `docs/`

### FR-2: Backend Foundation (FastAPI)
- Python 3.11+ with FastAPI
- Async SQLAlchemy with PostgreSQL (asyncpg)
- Redis for caching and rate limiting
- Structured logging with structlog
- Pydantic Settings for configuration
- Health endpoint: `GET /health` → `{"status": "ok", "service": "agent-hub"}`
- Version endpoint: `GET /api/v1/version` → `{"version": "0.1.0", "env": "..."}`
- OpenAPI documentation at `/docs`

### FR-3: Frontend Foundation (React + Vite)
- React 18 + TypeScript + Vite
- Tailwind CSS for styling
- React Router v6 with lazy-loaded pages
- Placeholder pages: Dashboard, Agents, API Keys, Usage, Documentation, Settings
- Vite proxy to backend at port 8000
- Path alias `@/` → `src/`

### FR-4: Database Foundation
- PostgreSQL 15 with async engine
- Alembic for migrations
- Initial system tables: `users` (minimal), `agents`, `api_keys`, `usage_events`
- Base model with common fields (id, created_at, updated_at)

### FR-5: Redis Foundation
- Redis 7 available for caching, rate limiting, temporary data
- Connection pooling with health checks
- Basic cache utility functions (get, set, delete, expire)

### FR-6: Docker & Development Environment
- `docker-compose.yml` with: PostgreSQL, Redis, Backend, Frontend
- Individual Dockerfiles per service
- Single `docker compose up` starts everything
- Volume mounts for hot reload in development

### FR-7: Configuration Management
- `.env.example` with all required variables and safe defaults
- Pydantic Settings class with validation
- Separate configs for: database, redis, app, server, cors, logging
- Never hardcode secrets

### FR-8: Logging & Error Handling
- Structured JSON logging (structlog)
- Request ID middleware (every request gets unique ID)
- Standardized error responses: `{"success": false, "error": {"code": "...", "message": "..."}, "request_id": "..."}`
- Access log middleware

### FR-9: Testing Foundation
- pytest + pytest-asyncio for backend
- Test database with fixtures
- Minimum: health endpoint test, config test, database connection test
- CI-ready test commands

### FR-10: CI/CD Pipeline
- GitHub Actions workflow
- Steps: lint → type-check → test → build
- Deployment targets: Vercel (frontend), Railway (backend + postgres + redis)

## Non-Functional Requirements

### NFR-1: Performance
- Backend response time < 100ms for health endpoints
- Database connection pooling (5 connections, 10 overflow)

### NFR-2: Security
- No secrets in code or version control
- CORS configured for allowed origins only
- Input validation via Pydantic

### NFR-3: Developer Experience
- README with complete setup instructions
- `docker compose up` = everything works
- Hot reload for both frontend and backend

## Acceptance Criteria
- [ ] GitHub repository initialized with proper .gitignore
- [ ] `docker compose up` starts all services successfully
- [ ] `GET /health` returns 200 with status ok
- [ ] `GET /api/v1/version` returns version info
- [ ] Frontend loads at localhost:3000
- [ ] PostgreSQL accepts connections
- [ ] Redis accepts connections
- [ ] Structured logs appear in console
- [ ] Tests pass via `pytest`
- [ ] CI pipeline runs on push
- [ ] README documents setup process
