"""
API Key management endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.database import get_db
from apps.api.app.core.deps import get_current_user
from apps.api.app.core.exceptions import NotFoundError
from apps.api.app.models.user import User
from apps.api.app.schemas.key import KeyCreateRequest, KeyCreateResponse, KeyListResponse, KeyResponse
from apps.api.app.services.key_manager import create_key, list_keys, revoke_key

router = APIRouter(prefix="/keys", tags=["API Keys"])


@router.post("", response_model=KeyCreateResponse, status_code=201)
async def create_api_key(
    body: KeyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new API key. The full key is only shown once."""
    api_key, full_key = await create_key(db, user=current_user, name=body.name)
    return KeyCreateResponse(
        id=api_key.id,
        name=api_key.name,
        key=full_key,
        key_prefix=api_key.key_prefix,
        created_at=api_key.created_at,
    )


@router.get("", response_model=KeyListResponse)
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all API keys for the current user."""
    keys = await list_keys(db, user=current_user)
    return KeyListResponse(
        keys=[KeyResponse.model_validate(k) for k in keys],
        total=len(keys),
    )


@router.delete("/{key_id}", status_code=204)
async def revoke_api_key(
    key_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke an API key."""
    success = await revoke_key(db, user=current_user, key_id=key_id)
    if not success:
        raise NotFoundError("API key not found")
