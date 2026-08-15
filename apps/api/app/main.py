"""
Agent Hub — Backend
FastAPI application entry point.

Startup order:
  1. Logging configured
  2. App created with OpenAPI metadata
  3. Middleware registered
  4. v1 API router mounted
  5. Root-level health kept for Docker healthchecks
"""

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.app.api.v1.router import router as v1_router
from apps.api.app.core.config import settings
from apps.api.app.core.exceptions import AppError, app_error_handler, unhandled_error_handler
from apps.api.app.core.logging import setup_logging
from apps.api.app.middleware.access_log import AccessLogMiddleware
from apps.api.app.middleware.request_id import RequestIDMiddleware

# ── 1. Logging ─────────────────────────────────────────────────────────────────
setup_logging(log_level=settings.LOG_LEVEL, json_logs=settings.LOG_JSON)
logger = structlog.get_logger(__name__)

# ── 2. App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {"name": "System", "description": "Health checks and version info."},
        {"name": "Agents", "description": "Agent registry and execution."},
        {"name": "Auth", "description": "Authentication and authorization."},
        {"name": "Usage", "description": "Usage metering and analytics."},
    ],
)

# ── 3. Middleware (outermost → innermost) ──────────────────────────────────────
app.add_middleware(RequestIDMiddleware)
app.add_middleware(AccessLogMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 4. Exception handlers ──────────────────────────────────────────────────────
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)

# ── 5. Routers ─────────────────────────────────────────────────────────────────
app.include_router(v1_router)


# ── 6. Root-level health (Docker HEALTHCHECK) ──────────────────────────────────
@app.get("/health", tags=["System"], include_in_schema=False)
async def health_root():
    return {"status": "ok", "service": "agent-hub"}


# ── 7. Startup / shutdown events ───────────────────────────────────────────────
@app.on_event("startup")
async def on_startup() -> None:
    # Create tables if they don't exist (dev mode)
    from apps.api.app.core.database import engine, Base
    import apps.api.app.models  # noqa: F401 — ensure all models loaded
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from apps.api.app.services.agent_registry import registry
    registry.discover_and_register()
    logger.info(
        "app.startup",
        name=settings.APP_NAME,
        version=settings.APP_VERSION,
        env=settings.APP_ENV,
        agents_registered=registry.count,
        docs="http://localhost:8000/docs",
    )


@app.on_event("shutdown")
async def on_shutdown() -> None:
    from apps.api.app.core.cache import close_redis_pool
    await close_redis_pool()
    logger.info("app.shutdown")
