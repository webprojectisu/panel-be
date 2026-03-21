"""
Appointment management service.
"""

from datetime import date, time
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models.appointment import Appointment, AppointmentStatus
from app.models.client import Client
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate


def _enrich(appointment: Appointment) -> Appointment:
    """Attach client_name as a transient attribute for response serialization."""
    if appointment.client:
        appointment.__dict__["client_name"] = appointment.client.full_name
    else:
        appointment.__dict__["client_name"] = None
    return appointment


def list_appointments(
    db: Session,
    dietitian_id: int,
    skip: int = 0,
    limit: int = 20,
    date_filter: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    client_id: Optional[int] = None,
    status: Optional[AppointmentStatus] = None,
) -> List[Appointment]:
    try:
        query = (
            db.query(Appointment)
            .join(Client, Appointment.client_id == Client.id)
            .filter(Appointment.dietitian_id == dietitian_id)
        )
        if date_filter is not None:
            query = query.filter(Appointment.appointment_date == date_filter)
        if start_date is not None:
            query = query.filter(Appointment.appointment_date >= start_date)
        if end_date is not None:
            query = query.filter(Appointment.appointment_date <= end_date)
        if client_id is not None:
            query = query.filter(Appointment.client_id == client_id)
        if status is not None:
            query = query.filter(Appointment.status == status)

        appointments = (
            query
            .order_by(Appointment.appointment_date, Appointment.start_time)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [_enrich(a) for a in appointments]
    except Exception as exc:
        raise exc


def create_appointment(
    db: Session, dietitian_id: int, data: AppointmentCreate
) -> Appointment:
    try:
        # Verify client belongs to this dietitian
        client: Client | None = db.get(Client, data.client_id)
        if client is None:
            raise NotFoundException(f"Client with id={data.client_id} not found.")
        if client.dietitian_id != dietitian_id:
            raise ForbiddenException("You do not have access to this client.")

        # Check for time conflicts on same day for same dietitian
        if data.end_time is not None:
            conflict = (
                db.query(Appointment)
                .filter(
                    Appointment.dietitian_id == dietitian_id,
                    Appointment.appointment_date == data.appointment_date,
                    Appointment.status != AppointmentStatus.cancelled,
                    Appointment.end_time.isnot(None),
                    Appointment.start_time < data.end_time,
                    Appointment.end_time > data.start_time,
                )
                .first()
            )
            if conflict is not None:
                raise ConflictException(
                    "There is an overlapping appointment at the specified time."
                )

        appointment = Appointment(
            dietitian_id=dietitian_id,
            client_id=data.client_id,
            appointment_date=data.appointment_date,
            start_time=data.start_time,
            end_time=data.end_time,
            notes=data.notes,
        )
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        return _enrich(appointment)
    except (NotFoundException, ForbiddenException, ConflictException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def get_appointment(
    db: Session, appointment_id: int, dietitian_id: int
) -> Appointment:
    try:
        appointment: Appointment | None = db.get(Appointment, appointment_id)
        if appointment is None:
            raise NotFoundException(f"Appointment with id={appointment_id} not found.")
        if appointment.dietitian_id != dietitian_id:
            raise ForbiddenException("You do not have access to this appointment.")
        return _enrich(appointment)
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        raise exc


def update_appointment(
    db: Session, appointment_id: int, dietitian_id: int, data: AppointmentUpdate
) -> Appointment:
    try:
        appointment = get_appointment(db, appointment_id, dietitian_id)
        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(appointment, field, value)
        db.commit()
        db.refresh(appointment)
        return _enrich(appointment)
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def delete_appointment(
    db: Session, appointment_id: int, dietitian_id: int
) -> None:
    try:
        appointment = get_appointment(db, appointment_id, dietitian_id)
        db.delete(appointment)
        db.commit()
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def get_today_appointments(db: Session, dietitian_id: int) -> List[Appointment]:
    try:
        today = date.today()
        appointments = (
            db.query(Appointment)
            .filter(
                Appointment.dietitian_id == dietitian_id,
                Appointment.appointment_date == today,
            )
            .order_by(Appointment.start_time)
            .all()
        )
        return [_enrich(a) for a in appointments]
    except Exception as exc:
        raise exc
