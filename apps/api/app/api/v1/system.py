"""
System endpoints — health checks, version info.
"""

from fastapi import APIRouter

from apps.api.app.core.config import settings

router = APIRouter(tags=["System"])


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "agent-hub"}


@router.get("/version")
async def version():
    """Version and environment info."""
    return {
        "version": settings.APP_VERSION,
        "env": settings.APP_ENV,
        "name": settings.APP_NAME,
    }
