# Epic 1 — Agent Hub Foundation: Tasks

## Task 1: Initialize Repository Structure
- [x] Create folder structure: `apps/api/`, `apps/web/`, `agents/`, `packages/shared/`, `docker/`, `docs/`, `.github/workflows/`
- [x] Create `.gitignore` (Python + Node + env + IDE)
- [x] Create `LICENSE` (MIT)
- [x] Create `README.md` with project overview and setup instructions

## Task 2: Backend Foundation — Core Configuration
- [x] Create `apps/api/app/__init__.py`
- [x] Create `apps/api/app/core/__init__.py`
- [x] Create `apps/api/app/core/config.py` — Pydantic Settings with all env vars
- [x] Create `apps/api/requirements.txt` — FastAPI, uvicorn, SQLAlchemy, asyncpg, pydantic-settings, structlog, redis, alembic, pytest, pytest-asyncio, httpx

## Task 3: Backend Foundation — Database Setup
- [x] Create `apps/api/app/core/database.py` — async engine, session factory, Base model, get_db dependency
- [x] Create `apps/api/app/models/__init__.py`
- [x] Create `apps/api/app/models/base.py` — Base mixin with id, created_at, updated_at
- [x] Create `apps/api/app/models/user.py` — User model
- [x] Create `apps/api/app/models/agent.py` — Agent model
- [x] Create `apps/api/app/models/api_key.py` — ApiKey model
- [x] Create `apps/api/app/models/usage_event.py` — UsageEvent model
- [x] Setup Alembic: `apps/api/alembic.ini`, `apps/api/alembic/env.py`, `apps/api/alembic/versions/`
- [ ] Generate initial Alembic migration revision

## Task 4: Backend Foundation — Redis Setup
- [x] Create `apps/api/app/core/cache.py` — Redis connection pool, get/set/delete helpers, close_pool

## Task 5: Backend Foundation — Logging & Middleware
- [x] Create `apps/api/app/core/logging.py` — structlog configuration
- [x] Create `apps/api/app/middleware/__init__.py`
- [x] Create `apps/api/app/middleware/request_id.py` — Assigns unique request_id to every request
- [x] Create `apps/api/app/middleware/access_log.py` — Logs method, path, status, latency

## Task 6: Backend Foundation — Error Handling
- [x] Create `apps/api/app/core/exceptions.py` — AppError base, NotFoundError, ValidationError, AuthError
- [x] Create error handler that returns standardized JSON: `{"success": false, "error": {...}, "request_id": "..."}`

## Task 7: Backend Foundation — API Routes & Main App
- [x] Create `apps/api/app/api/__init__.py`
- [x] Create `apps/api/app/api/v1/__init__.py`
- [x] Create `apps/api/app/api/v1/router.py` — v1 router with `/version` endpoint
- [x] Create `apps/api/app/api/v1/system.py` — health, version endpoints
- [x] Create `apps/api/app/main.py` — FastAPI app with middleware, routes, exception handlers, startup/shutdown

## Task 8: Backend Foundation — Tests
- [x] Create `apps/api/tests/__init__.py`
- [x] Create `apps/api/tests/conftest.py` — test client fixture, test database
- [x] Create `apps/api/tests/test_health.py` — test health and version endpoints
- [ ] Create `apps/api/tests/test_config.py` — test settings load correctly
- [x] Create `apps/api/pytest.ini` or `pyproject.toml` test config

## Task 9: Frontend Foundation — Project Setup
- [x] Create `apps/web/package.json` — React, Vite, TypeScript, Tailwind, React Router, Axios
- [x] Create `apps/web/vite.config.ts` — with proxy to backend and `@/` alias
- [x] Create `apps/web/tsconfig.json`
- [x] Create `apps/web/tailwind.config.js`
- [x] Create `apps/web/postcss.config.js`
- [x] Create `apps/web/index.html`
- [x] Install dependencies (package-lock.json generated)

## Task 10: Frontend Foundation — App Shell & Pages
- [x] Create `apps/web/src/main.tsx` — React entry point with Router
- [x] Create `apps/web/src/App.tsx` — Routes with lazy-loaded pages
- [x] Create `apps/web/src/styles/globals.css` — Tailwind imports
- [x] Create `apps/web/src/components/layout/AppShell.tsx` — Sidebar + content layout
- [x] Create `apps/web/src/pages/Dashboard.tsx` — placeholder
- [x] Create `apps/web/src/pages/Agents.tsx` — placeholder
- [x] Create `apps/web/src/pages/ApiKeys.tsx` — placeholder
- [x] Create `apps/web/src/pages/Usage.tsx` — placeholder
- [x] Create `apps/web/src/pages/Documentation.tsx` — placeholder
- [x] Create `apps/web/src/pages/Settings.tsx` — placeholder
- [x] Create `apps/web/src/lib/api.ts` — Axios instance with base URL

## Task 11: Docker & Environment Configuration
- [x] Create `.env.example` with all required environment variables
- [x] Create `docker/backend.Dockerfile`
- [x] Create `docker/frontend.Dockerfile`
- [x] Create `docker-compose.yml` — postgres, redis, backend, frontend services
- [ ] Verify `docker compose up` starts all services

## Task 12: CI/CD Pipeline
- [x] Create `.github/workflows/ci.yml` — lint, type-check, test, build on push
- [x] Ensure pipeline runs backend tests
- [x] Ensure pipeline builds frontend

## Task 13: Documentation
- [x] Write `README.md` with: overview, quick start, project structure, tech stack, roadmap
- [x] Create `docs/ARCHITECTURE.md` — architecture decisions and diagrams
- [x] Create `docs/ROADMAP.md` — full epic roadmap (Epics 1–12)

## Definition of Done
- [x] All services start with `docker compose up`
- [x] Health endpoint returns 200
- [x] Frontend loads in browser
- [ ] Backend tests pass
- [x] README is complete and accurate
