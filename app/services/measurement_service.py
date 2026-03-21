"""
Body measurement management service.
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.client import Client
from app.models.measurement import Measurement
from app.schemas.measurement import MeasurementCreate


def _verify_client(db: Session, client_id: int, dietitian_id: int) -> Client:
    client: Client | None = db.get(Client, client_id)
    if client is None:
        raise NotFoundException(f"Client with id={client_id} not found.")
    if client.dietitian_id != dietitian_id:
        raise ForbiddenException("You do not have access to this client.")
    return client


def list_measurements(
    db: Session,
    client_id: int,
    dietitian_id: int,
    skip: int = 0,
    limit: int = 20,
) -> List[Measurement]:
    try:
        _verify_client(db, client_id, dietitian_id)
        return (
            db.query(Measurement)
            .filter(Measurement.client_id == client_id)
            .order_by(Measurement.recorded_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        raise exc


def create_measurement(
    db: Session, client_id: int, dietitian_id: int, data: MeasurementCreate
) -> Measurement:
    """
    Create a body measurement snapshot for a client.

    If height_cm and weight_kg are provided but bmi is not, auto-compute:
        bmi = weight_kg / (height_cm / 100) ** 2
    """
    try:
        _verify_client(db, client_id, dietitian_id)

        bmi = data.bmi
        if bmi is None and data.height_cm and data.weight_kg:
            height_m = data.height_cm / 100.0
            bmi = round(data.weight_kg / (height_m ** 2), 2)

        recorded_at = data.recorded_at or datetime.now(timezone.utc)

        measurement = Measurement(
            client_id=client_id,
            height_cm=data.height_cm,
            weight_kg=data.weight_kg,
            bmi=bmi,
            body_fat_percentage=data.body_fat_percentage,
            waist_cm=data.waist_cm,
            hip_cm=data.hip_cm,
            chest_cm=data.chest_cm,
            recorded_at=recorded_at,
            notes=data.notes,
        )
        db.add(measurement)
        db.commit()
        db.refresh(measurement)
        return measurement
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def get_latest_measurement(
    db: Session, client_id: int, dietitian_id: int
) -> Optional[Measurement]:
    try:
        _verify_client(db, client_id, dietitian_id)
        return (
            db.query(Measurement)
            .filter(Measurement.client_id == client_id)
            .order_by(Measurement.recorded_at.desc())
            .first()
        )
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        raise exc


def delete_measurement(
    db: Session, measurement_id: int, dietitian_id: int
) -> None:
    try:
        measurement: Measurement | None = db.get(Measurement, measurement_id)
        if measurement is None:
            raise NotFoundException(f"Measurement with id={measurement_id} not found.")
        # Verify via client ownership
        _verify_client(db, measurement.client_id, dietitian_id)
        db.delete(measurement)
        db.commit()
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc
