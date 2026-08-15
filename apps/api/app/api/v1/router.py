"""
API v1 router — aggregates all v1 sub-routers.
"""

from fastapi import APIRouter

from apps.api.app.api.v1.admin import router as admin_router
from apps.api.app.api.v1.agents import router as agents_router
from apps.api.app.api.v1.auth import router as auth_router
from apps.api.app.api.v1.gateway import router as gateway_router
from apps.api.app.api.v1.keys import router as keys_router
from apps.api.app.api.v1.system import router as system_router
from apps.api.app.api.v1.usage import router as usage_router

router = APIRouter(prefix="/api/v1")

router.include_router(system_router)
router.include_router(auth_router)
router.include_router(keys_router)
router.include_router(agents_router)
router.include_router(gateway_router)
router.include_router(usage_router)
router.include_router(admin_router)
