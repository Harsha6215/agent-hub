"""
Usage analytics endpoints — track agent execution metrics.
"""

from datetime import date, datetime, timezone, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.database import get_db
from apps.api.app.core.deps import get_current_user
from apps.api.app.models.usage_event import UsageEvent
from apps.api.app.models.user import User
from apps.api.app.schemas.usage import (
    AgentUsageItem,
    AgentUsageResponse,
    DailyUsageItem,
    DailyUsageResponse,
    UsageSummaryResponse,
)

router = APIRouter(prefix="/usage", tags=["Usage"])


@router.get("", response_model=UsageSummaryResponse)
async def get_usage_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get usage summary for the current month."""
    now = datetime.now(timezone.utc)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    base_query = select(UsageEvent).where(
        UsageEvent.user_id == current_user.id,
        UsageEvent.created_at >= start_of_month,
    )

    # Total requests
    total_q = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(total_q)).scalar() or 0

    # Successful
    success_q = select(func.count()).select_from(
        base_query.where(UsageEvent.status == "success").subquery()
    )
    successful = (await db.execute(success_q)).scalar() or 0

    # Total cost
    cost_q = select(func.coalesce(func.sum(UsageEvent.cost_paisa), 0)).where(
        UsageEvent.user_id == current_user.id,
        UsageEvent.created_at >= start_of_month,
    )
    total_cost = (await db.execute(cost_q)).scalar() or 0

    return UsageSummaryResponse(
        total_requests=total,
        successful_requests=successful,
        failed_requests=total - successful,
        total_cost_paisa=total_cost,
        period=now.strftime("%Y-%m"),
    )


@router.get("/daily", response_model=DailyUsageResponse)
async def get_daily_usage(
    days: int = Query(30, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get daily usage breakdown for the last N days."""
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(
            cast(UsageEvent.created_at, Date).label("day"),
            func.count().label("requests"),
            func.coalesce(func.sum(UsageEvent.cost_paisa), 0).label("cost"),
        )
        .where(
            UsageEvent.user_id == current_user.id,
            UsageEvent.created_at >= start_date,
        )
        .group_by(cast(UsageEvent.created_at, Date))
        .order_by(cast(UsageEvent.created_at, Date))
    )

    rows = result.all()
    daily = [DailyUsageItem(date=row.day, requests=row.requests, cost_paisa=row.cost) for row in rows]
    total = sum(d.requests for d in daily)

    return DailyUsageResponse(daily=daily, total_requests=total)


@router.get("/by-agent", response_model=AgentUsageResponse)
async def get_usage_by_agent(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get usage grouped by agent for the current month."""
    now = datetime.now(timezone.utc)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    result = await db.execute(
        select(
            UsageEvent.agent_slug,
            func.count().label("requests"),
            func.coalesce(func.sum(UsageEvent.cost_paisa), 0).label("cost"),
        )
        .where(
            UsageEvent.user_id == current_user.id,
            UsageEvent.created_at >= start_of_month,
        )
        .group_by(UsageEvent.agent_slug)
        .order_by(func.count().desc())
    )

    rows = result.all()
    by_agent = [AgentUsageItem(agent_slug=row.agent_slug, requests=row.requests, cost_paisa=row.cost) for row in rows]
    total = sum(a.requests for a in by_agent)

    return AgentUsageResponse(by_agent=by_agent, total_requests=total)
