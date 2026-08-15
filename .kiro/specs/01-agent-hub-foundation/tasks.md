# Epic 1 — Agent Hub Foundation: Tasks

## Task 1: Initialize Repository Structure
- [ ] Create folder structure: `apps/api/`, `apps/web/`, `agents/`, `packages/shared/`, `docker/`, `docs/`, `.github/workflows/`
- [ ] Create `.gitignore` (Python + Node + env + IDE)
- [ ] Create `LICENSE` (MIT)
- [ ] Create `README.md` with project overview and setup instructions

## Task 2: Backend Foundation — Core Configuration
- [ ] Create `apps/api/app/__init__.py`
- [ ] Create `apps/api/app/core/__init__.py`
- [ ] Create `apps/api/app/core/config.py` — Pydantic Settings with all env vars
- [ ] Create `apps/api/requirements.txt` — FastAPI, uvicorn, SQLAlchemy, asyncpg, pydantic-settings, structlog, redis, alembic, pytest, pytest-asyncio, httpx

## Task 3: Backend Foundation — Database Setup
- [ ] Create `apps/api/app/core/database.py` — async engine, session factory, Base model, get_db dependency
- [ ] Create `apps/api/app/models/__init__.py`
- [ ] Create `apps/api/app/models/base.py` — Base mixin with id, created_at, updated_at
- [ ] Create `apps/api/app/models/user.py` — User model
- [ ] Create `apps/api/app/models/agent.py` — Agent model
- [ ] Create `apps/api/app/models/api_key.py` — ApiKey model
- [ ] Create `apps/api/app/models/usage_event.py` — UsageEvent model
- [ ] Setup Alembic: `apps/api/alembic.ini`, `apps/api/alembic/env.py`, `apps/api/alembic/versions/`

## Task 4: Backend Foundation — Redis Setup
- [ ] Create `apps/api/app/core/cache.py` — Redis connection pool, get/set/delete helpers, close_pool

## Task 5: Backend Foundation — Logging & Middleware
- [ ] Create `apps/api/app/core/logging.py` — structlog configuration
- [ ] Create `apps/api/app/middleware/__init__.py`
- [ ] Create `apps/api/app/middleware/request_id.py` — Assigns unique request_id to every request
- [ ] Create `apps/api/app/middleware/access_log.py` — Logs method, path, status, latency

## Task 6: Backend Foundation — Error Handling
- [ ] Create `apps/api/app/core/exceptions.py` — AppError base, NotFoundError, ValidationError, AuthError
- [ ] Create error handler that returns standardized JSON: `{"success": false, "error": {...}, "request_id": "..."}`

## Task 7: Backend Foundation — API Routes & Main App
- [ ] Create `apps/api/app/api/__init__.py`
- [ ] Create `apps/api/app/api/v1/__init__.py`
- [ ] Create `apps/api/app/api/v1/router.py` — v1 router with `/version` endpoint
- [ ] Create `apps/api/app/api/v1/system.py` — health, version endpoints
- [ ] Create `apps/api/app/main.py` — FastAPI app with middleware, routes, exception handlers, startup/shutdown

## Task 8: Backend Foundation — Tests
- [ ] Create `apps/api/tests/__init__.py`
- [ ] Create `apps/api/tests/conftest.py` — test client fixture, test database
- [ ] Create `apps/api/tests/test_health.py` — test health and version endpoints
- [ ] Create `apps/api/tests/test_config.py` — test settings load correctly
- [ ] Create `apps/api/pytest.ini` or `pyproject.toml` test config

## Task 9: Frontend Foundation — Project Setup
- [ ] Create `apps/web/package.json` — React, Vite, TypeScript, Tailwind, React Router, Axios
- [ ] Create `apps/web/vite.config.ts` — with proxy to backend and `@/` alias
- [ ] Create `apps/web/tsconfig.json`
- [ ] Create `apps/web/tailwind.config.js`
- [ ] Create `apps/web/postcss.config.js`
- [ ] Create `apps/web/index.html`

## Task 10: Frontend Foundation — App Shell & Pages
- [ ] Create `apps/web/src/main.tsx` — React entry point with Router
- [ ] Create `apps/web/src/App.tsx` — Routes with lazy-loaded pages
- [ ] Create `apps/web/src/styles/globals.css` — Tailwind imports
- [ ] Create `apps/web/src/components/layout/AppShell.tsx` — Sidebar + content layout
- [ ] Create `apps/web/src/pages/Dashboard.tsx` — placeholder
- [ ] Create `apps/web/src/pages/Agents.tsx` — placeholder
- [ ] Create `apps/web/src/pages/ApiKeys.tsx` — placeholder
- [ ] Create `apps/web/src/pages/Usage.tsx` — placeholder
- [ ] Create `apps/web/src/pages/Documentation.tsx` — placeholder
- [ ] Create `apps/web/src/pages/Settings.tsx` — placeholder
- [ ] Create `apps/web/src/lib/api.ts` — Axios instance with base URL

## Task 11: Docker & Environment Configuration
- [ ] Create `.env.example` with all required environment variables
- [ ] Create `docker/backend.Dockerfile`
- [ ] Create `docker/frontend.Dockerfile`
- [ ] Create `docker-compose.yml` — postgres, redis, backend, frontend services
- [ ] Verify `docker compose up` starts all services

## Task 12: CI/CD Pipeline
- [ ] Create `.github/workflows/ci.yml` — lint, type-check, test, build on push
- [ ] Ensure pipeline runs backend tests
- [ ] Ensure pipeline builds frontend

## Task 13: Documentation
- [ ] Write `README.md` with: overview, quick start, project structure, tech stack, roadmap
- [ ] Create `docs/ARCHITECTURE.md` — architecture decisions and diagrams
- [ ] Create `docs/ROADMAP.md` — full epic roadmap (Epics 1–12)

## Definition of Done
- [ ] All services start with `docker compose up`
- [ ] Health endpoint returns 200
- [ ] Frontend loads in browser
- [ ] Backend tests pass
- [ ] README is complete and accurate
