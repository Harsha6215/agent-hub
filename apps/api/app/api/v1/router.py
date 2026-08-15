"""
API v1 router — aggregates all v1 sub-routers.
"""

from fastapi import APIRouter

from apps.api.app.api.v1.system import router as system_router

router = APIRouter(prefix="/api/v1")

router.include_router(system_router)
