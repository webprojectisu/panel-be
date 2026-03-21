"""
Dashboard statistics endpoint.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.dashboard import (
    ClientDistribution,
    DashboardStatsResponse,
    RevenueTrendItem,
    TodayAppointmentItem,
)
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    period: str = Query(default="monthly"),
) -> DashboardStatsResponse:
    stats = dashboard_service.get_stats(db, current_user.id, period=period)

    today_appointments = [
        TodayAppointmentItem(
            id=a["id"],
            client_name=a["client_name"],
            start_time=a["start_time"],
            end_time=a["end_time"],
            status=a["status"],
        )
        for a in stats["today_appointments"]
    ]

    revenue_trend = [
        RevenueTrendItem(month=item["month"], amount=item["amount"])
        for item in stats["revenue_trend"]
    ]

    dist = stats["client_distribution"]
    client_distribution = ClientDistribution(
        weight_loss=dist.get("weight_loss", 0),
        weight_gain=dist.get("weight_gain", 0),
        healthy_eating=dist.get("healthy_eating", 0),
        sports_nutrition=dist.get("sports_nutrition", 0),
        other=dist.get("other", 0),
    )

    return DashboardStatsResponse(
        active_clients=stats["active_clients"],
        weekly_appointments=stats["weekly_appointments"],
        monthly_revenue=stats["monthly_revenue"],
        currency=stats["currency"],
        success_rate=stats["success_rate"],
        new_clients_this_month=stats["new_clients_this_month"],
        today_appointments=today_appointments,
        revenue_trend=revenue_trend,
        client_distribution=client_distribution,
    )
