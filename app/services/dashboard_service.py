"""
Dashboard statistics service.
"""

from datetime import date, timedelta
from typing import Any, Dict, List

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, AppointmentStatus
from app.models.client import Client
from app.models.diet_plan import DietPlan
from app.models.payment import Payment, PaymentStatus
from app.services.appointment_service import get_today_appointments


def get_stats(db: Session, dietitian_id: int, period: str = "monthly") -> Dict[str, Any]:
    """
    Compile dashboard statistics for the given dietitian.

    Returns a dict that maps directly to DashboardStatsResponse.
    """
    try:
        today = date.today()
        current_year = today.year
        current_month = today.month

        # ------------------------------------------------------------------ #
        # Active clients
        # ------------------------------------------------------------------ #
        active_clients = (
            db.query(func.count(Client.id))
            .filter(Client.dietitian_id == dietitian_id)
            .scalar()
        ) or 0

        # ------------------------------------------------------------------ #
        # Weekly appointments (Mon – Sun of the current week)
        # ------------------------------------------------------------------ #
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        weekly_appointments = (
            db.query(func.count(Appointment.id))
            .filter(
                Appointment.dietitian_id == dietitian_id,
                Appointment.appointment_date >= week_start,
                Appointment.appointment_date <= week_end,
            )
            .scalar()
        ) or 0

        # ------------------------------------------------------------------ #
        # Monthly revenue (completed payments this month)
        # ------------------------------------------------------------------ #
        monthly_revenue_result = (
            db.query(func.sum(Payment.amount))
            .filter(
                Payment.dietitian_id == dietitian_id,
                Payment.status == PaymentStatus.completed,
                extract("year", Payment.payment_date) == current_year,
                extract("month", Payment.payment_date) == current_month,
            )
            .scalar()
        )
        monthly_revenue = float(monthly_revenue_result) if monthly_revenue_result else 0.0

        # Determine the most-used currency for this dietitian
        currency_result = (
            db.query(Payment.currency, func.count(Payment.id).label("cnt"))
            .filter(Payment.dietitian_id == dietitian_id)
            .group_by(Payment.currency)
            .order_by(func.count(Payment.id).desc())
            .first()
        )
        currency = currency_result[0] if currency_result else "TRY"

        # ------------------------------------------------------------------ #
        # Success rate: % of appointments completed in last 30 days
        # ------------------------------------------------------------------ #
        thirty_days_ago = today - timedelta(days=30)
        total_recent = (
            db.query(func.count(Appointment.id))
            .filter(
                Appointment.dietitian_id == dietitian_id,
                Appointment.appointment_date >= thirty_days_ago,
                Appointment.appointment_date <= today,
            )
            .scalar()
        ) or 0

        completed_recent = (
            db.query(func.count(Appointment.id))
            .filter(
                Appointment.dietitian_id == dietitian_id,
                Appointment.appointment_date >= thirty_days_ago,
                Appointment.appointment_date <= today,
                Appointment.status == AppointmentStatus.completed,
            )
            .scalar()
        ) or 0

        success_rate = (
            round((completed_recent / total_recent) * 100, 1) if total_recent > 0 else 0.0
        )

        # ------------------------------------------------------------------ #
        # New clients this month
        # ------------------------------------------------------------------ #
        new_clients_this_month = (
            db.query(func.count(Client.id))
            .filter(
                Client.dietitian_id == dietitian_id,
                extract("year", Client.created_at) == current_year,
                extract("month", Client.created_at) == current_month,
            )
            .scalar()
        ) or 0

        # ------------------------------------------------------------------ #
        # Today's appointments
        # ------------------------------------------------------------------ #
        today_appts = get_today_appointments(db, dietitian_id)
        today_appointments_list = []
        for appt in today_appts:
            client_name = appt.__dict__.get("client_name") or (
                appt.client.full_name if appt.client else "Unknown"
            )
            today_appointments_list.append(
                {
                    "id": appt.id,
                    "client_name": client_name,
                    "start_time": appt.start_time,
                    "end_time": appt.end_time,
                    "status": appt.status,
                }
            )

        # ------------------------------------------------------------------ #
        # Revenue trend: last 6 months
        # ------------------------------------------------------------------ #
        revenue_trend: List[Dict[str, Any]] = []
        for i in range(5, -1, -1):
            month = current_month - i
            year = current_year
            while month <= 0:
                month += 12
                year -= 1

            month_total = (
                db.query(func.sum(Payment.amount))
                .filter(
                    Payment.dietitian_id == dietitian_id,
                    Payment.status == PaymentStatus.completed,
                    extract("year", Payment.payment_date) == year,
                    extract("month", Payment.payment_date) == month,
                )
                .scalar()
            )
            revenue_trend.append(
                {
                    "month": f"{year}-{month:02d}",
                    "amount": float(month_total) if month_total else 0.0,
                }
            )

        # ------------------------------------------------------------------ #
        # Client distribution: categorize by diet plan title keywords
        # ------------------------------------------------------------------ #
        distribution = {
            "weight_loss": 0,
            "weight_gain": 0,
            "healthy_eating": 0,
            "sports_nutrition": 0,
            "other": 0,
        }

        plans = (
            db.query(DietPlan.title)
            .filter(DietPlan.dietitian_id == dietitian_id)
            .all()
        )
        for (title,) in plans:
            title_lower = title.lower()
            if any(kw in title_lower for kw in ["kilo verme", "weight loss", "zayıflama"]):
                distribution["weight_loss"] += 1
            elif any(kw in title_lower for kw in ["kilo alma", "weight gain", "kilo artırma"]):
                distribution["weight_gain"] += 1
            elif any(kw in title_lower for kw in ["sağlıklı", "healthy", "beslenme"]):
                distribution["healthy_eating"] += 1
            elif any(kw in title_lower for kw in ["spor", "sport", "egzersiz", "fitness"]):
                distribution["sports_nutrition"] += 1
            else:
                distribution["other"] += 1

        return {
            "active_clients": active_clients,
            "weekly_appointments": weekly_appointments,
            "monthly_revenue": monthly_revenue,
            "currency": currency,
            "success_rate": success_rate,
            "new_clients_this_month": new_clients_this_month,
            "today_appointments": today_appointments_list,
            "revenue_trend": revenue_trend,
            "client_distribution": distribution,
        }
    except Exception as exc:
        raise exc
