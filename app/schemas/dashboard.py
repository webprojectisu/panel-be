"""
Dashboard statistics response schemas.
"""

from datetime import time
from typing import List, Optional

from pydantic import BaseModel

from app.models.appointment import AppointmentStatus


class TodayAppointmentItem(BaseModel):
    id: int
    client_name: str
    start_time: time
    end_time: Optional[time] = None
    status: AppointmentStatus


class RevenueTrendItem(BaseModel):
    month: str   # e.g. "2026-01"
    amount: float


class ClientDistribution(BaseModel):
    weight_loss: int = 0
    weight_gain: int = 0
    healthy_eating: int = 0
    sports_nutrition: int = 0
    other: int = 0


class DashboardStatsResponse(BaseModel):
    active_clients: int
    weekly_appointments: int
    monthly_revenue: float
    currency: str
    success_rate: float
    new_clients_this_month: int
    today_appointments: List[TodayAppointmentItem]
    revenue_trend: List[RevenueTrendItem]
    client_distribution: ClientDistribution
