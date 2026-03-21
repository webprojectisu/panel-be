"""
Client management service.
"""

from datetime import date
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.appointment import Appointment, AppointmentStatus
from app.models.client import Client, Gender
from app.models.diet_plan import DietPlan, DietPlanStatus
from app.models.measurement import Measurement
from app.models.payment import Payment, PaymentStatus
from app.schemas.client import ClientCreate, ClientUpdate


def list_clients(
    db: Session,
    dietitian_id: int,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    gender: Optional[Gender] = None,
) -> List[Client]:
    """Return clients belonging to *dietitian_id*, with optional filters."""
    try:
        query = db.query(Client).filter(Client.dietitian_id == dietitian_id)
        if search:
            pattern = f"%{search}%"
            query = query.filter(
                Client.full_name.ilike(pattern) | Client.email.ilike(pattern)
            )
        if gender is not None:
            query = query.filter(Client.gender == gender)
        return query.order_by(Client.full_name).offset(skip).limit(limit).all()
    except Exception as exc:
        raise exc


def create_client(db: Session, dietitian_id: int, data: ClientCreate) -> Client:
    """Create a new client for *dietitian_id*."""
    try:
        client = Client(
            dietitian_id=dietitian_id,
            full_name=data.full_name,
            email=data.email,
            phone=data.phone,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            notes=data.notes,
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        return client
    except Exception as exc:
        db.rollback()
        raise exc


def get_client(db: Session, client_id: int, dietitian_id: int) -> Client:
    """
    Return a client by ID.

    Raises NotFoundException if not found, ForbiddenException if owned by
    a different dietitian (prevents information leakage).
    """
    try:
        client: Client | None = db.get(Client, client_id)
        if client is None:
            raise NotFoundException(f"Client with id={client_id} not found.")
        if client.dietitian_id != dietitian_id:
            raise ForbiddenException("You do not have access to this client.")
        return client
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        raise exc


def update_client(
    db: Session, client_id: int, dietitian_id: int, data: ClientUpdate
) -> Client:
    """Update client fields (partial update)."""
    try:
        client = get_client(db, client_id, dietitian_id)
        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(client, field, value)
        db.commit()
        db.refresh(client)
        return client
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def delete_client(db: Session, client_id: int, dietitian_id: int) -> None:
    """Delete a client and cascade-delete all related records."""
    try:
        client = get_client(db, client_id, dietitian_id)
        db.delete(client)
        db.commit()
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def get_client_summary(db: Session, client_id: int, dietitian_id: int) -> dict:
    """
    Aggregate summary data for a client dashboard card.

    Returns a dict suitable for ClientSummaryResponse.
    """
    try:
        client = get_client(db, client_id, dietitian_id)

        # Latest measurement
        latest_measurement = (
            db.query(Measurement)
            .filter(Measurement.client_id == client_id)
            .order_by(Measurement.recorded_at.desc())
            .first()
        )

        # Active diet plan
        active_diet_plan = (
            db.query(DietPlan)
            .filter(
                DietPlan.client_id == client_id,
                DietPlan.status == DietPlanStatus.active,
            )
            .first()
        )

        # Upcoming scheduled appointments
        today = date.today()
        upcoming_appointments = (
            db.query(Appointment)
            .filter(
                Appointment.client_id == client_id,
                Appointment.status == AppointmentStatus.scheduled,
                Appointment.appointment_date >= today,
            )
            .order_by(Appointment.appointment_date, Appointment.start_time)
            .all()
        )

        # Payment balance (sum of completed payments)
        result = (
            db.query(func.sum(Payment.amount))
            .filter(
                Payment.client_id == client_id,
                Payment.status == PaymentStatus.completed,
            )
            .scalar()
        )
        payment_balance = float(result) if result is not None else 0.0

        return {
            "client": client,
            "latest_measurement": latest_measurement,
            "active_diet_plan": active_diet_plan,
            "upcoming_appointments": upcoming_appointments,
            "payment_balance": payment_balance,
        }
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        raise exc
