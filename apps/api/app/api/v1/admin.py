"""
Admin analytics endpoints — platform-wide metrics.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.database import get_db
from apps.api.app.core.deps import get_current_admin
from apps.api.app.models.usage_event import UsageEvent
from apps.api.app.models.user import User
from apps.api.app.models.agent import Agent

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/analytics/overview")
async def analytics_overview(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Platform overview: total users, total calls, estimated revenue."""
    now = datetime.now(timezone.utc)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_users = (await db.execute(select(func.count()).select_from(User))).scalar() or 0
    total_calls = (await db.execute(select(func.count()).select_from(UsageEvent))).scalar() or 0
    monthly_calls = (await db.execute(
        select(func.count()).where(UsageEvent.created_at >= start_of_month)
    )).scalar() or 0
    monthly_revenue = (await db.execute(
        select(func.coalesce(func.sum(UsageEvent.cost_paisa), 0)).where(
            UsageEvent.created_at >= start_of_month
        )
    )).scalar() or 0

    return {
        "total_users": total_users,
        "total_calls": total_calls,
        "monthly_calls": monthly_calls,
        "monthly_revenue_paisa": monthly_revenue,
        "monthly_revenue_inr": round(monthly_revenue / 100, 2),
    }


@router.get("/analytics/agents")
async def analytics_agents(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Top agents by usage."""
    result = await db.execute(
        select(
            UsageEvent.agent_slug,
            func.count().label("total_calls"),
            func.coalesce(func.sum(UsageEvent.cost_paisa), 0).label("revenue_paisa"),
        )
        .group_by(UsageEvent.agent_slug)
        .order_by(func.count().desc())
        .limit(20)
    )

    rows = result.all()
    return {
        "agents": [
            {
                "slug": row.agent_slug,
                "total_calls": row.total_calls,
                "revenue_paisa": row.revenue_paisa,
            }
            for row in rows
        ]
    }


@router.get("/beta-metrics")
async def beta_metrics(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Beta program metrics for product decisions."""
    from datetime import timedelta

    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)

    registered_users = (await db.execute(select(func.count()).select_from(User))).scalar() or 0

    from apps.api.app.models.api_key import ApiKey
    api_keys_created = (await db.execute(select(func.count()).select_from(ApiKey))).scalar() or 0

    total_calls = (await db.execute(select(func.count()).select_from(UsageEvent))).scalar() or 0
    calls_24h = (await db.execute(
        select(func.count()).where(UsageEvent.created_at >= day_ago)
    )).scalar() or 0
    calls_7d = (await db.execute(
        select(func.count()).where(UsageEvent.created_at >= week_ago)
    )).scalar() or 0

    # Unique users with calls
    unique_users = (await db.execute(
        select(func.count(func.distinct(UsageEvent.user_id))).where(UsageEvent.user_id.isnot(None))
    )).scalar() or 0

    # Most used agent
    most_used_q = await db.execute(
        select(UsageEvent.agent_slug, func.count().label("cnt"))
        .group_by(UsageEvent.agent_slug)
        .order_by(func.count().desc())
        .limit(1)
    )
    most_used_row = most_used_q.first()
    most_used_agent = most_used_row.agent_slug if most_used_row else None

    return {
        "registered_users": registered_users,
        "api_keys_created": api_keys_created,
        "total_calls": total_calls,
        "calls_last_24h": calls_24h,
        "calls_last_7d": calls_7d,
        "unique_api_users": unique_users,
        "most_used_agent": most_used_agent,
    }
