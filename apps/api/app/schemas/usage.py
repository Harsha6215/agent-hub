"""
Usage schemas — response models for usage analytics.
"""

from datetime import date, datetime
from pydantic import BaseModel


class UsageSummaryResponse(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_cost_paisa: int
    period: str  # e.g., "2026-08"


class DailyUsageItem(BaseModel):
    date: date
    requests: int
    cost_paisa: int


class DailyUsageResponse(BaseModel):
    daily: list[DailyUsageItem]
    total_requests: int


class AgentUsageItem(BaseModel):
    agent_slug: str
    requests: int
    cost_paisa: int


class AgentUsageResponse(BaseModel):
    by_agent: list[AgentUsageItem]
    total_requests: int
