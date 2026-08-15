"""
Agent CRUD endpoints.
"""

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.database import get_db
from apps.api.app.core.exceptions import NotFoundError, ValidationError
from apps.api.app.models.agent import Agent
from apps.api.app.schemas.agent import (
    AgentCreate,
    AgentListResponse,
    AgentResponse,
    AgentUpdate,
)
from apps.api.app.services.agent_registry import registry

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("", response_model=AgentListResponse)
async def list_agents(
    category: str | None = Query(None, description="Filter by category"),
    is_public: bool = Query(True, description="Only show public agents"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: AsyncSession = Depends(get_db),
):
    """List all active agents in the catalog (paginated)."""
    query = select(Agent).where(Agent.is_active == True)
    if is_public:
        query = query.where(Agent.is_public == True)
    if category:
        query = query.where(Agent.category == category)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Apply pagination
    query = query.order_by(Agent.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    agents = result.scalars().all()

    return AgentListResponse(
        agents=[AgentResponse.model_validate(a) for a in agents],
        total=total,
    )


@router.get("/{slug}", response_model=AgentResponse)
async def get_agent(slug: str, db: AsyncSession = Depends(get_db)):
    """Get agent details by slug."""
    result = await db.execute(select(Agent).where(Agent.slug == slug))
    agent = result.scalar_one_or_none()
    if not agent:
        raise NotFoundError(f"Agent '{slug}' not found")
    return AgentResponse.model_validate(agent)


@router.get("/{slug}/docs")
async def get_agent_docs(slug: str):
    """Get auto-generated documentation for an agent."""
    agent_instance = registry.get(slug)
    if not agent_instance:
        raise NotFoundError(f"Agent '{slug}' not found in registry")
    return agent_instance.get_documentation()


@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(body: AgentCreate, db: AsyncSession = Depends(get_db)):
    """Create a new agent entry (admin)."""
    # Check for duplicate slug
    existing = await db.execute(select(Agent).where(Agent.slug == body.slug))
    if existing.scalar_one_or_none():
        raise ValidationError(f"Agent with slug '{body.slug}' already exists")

    agent = Agent(**body.model_dump())
    db.add(agent)
    await db.flush()
    await db.refresh(agent)
    logger.info("agent.created", slug=agent.slug)
    return AgentResponse.model_validate(agent)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID, body: AgentUpdate, db: AsyncSession = Depends(get_db)
):
    """Update an existing agent (admin)."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise NotFoundError("Agent not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    await db.flush()
    await db.refresh(agent)
    logger.info("agent.updated", slug=agent.slug)
    return AgentResponse.model_validate(agent)


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: UUID, db: AsyncSession = Depends(get_db)):
    """Soft-delete an agent (admin)."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise NotFoundError("Agent not found")

    agent.is_active = False
    await db.flush()
    logger.info("agent.deleted", slug=agent.slug)
