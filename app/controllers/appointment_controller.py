"""
Appointment management endpoints.

IMPORTANT: The /today route MUST be registered before /{appointment_id}
to avoid FastAPI treating "today" as a path parameter.
"""

from datetime import date
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.appointment import AppointmentStatus
from app.models.user import User
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
)
from app.services import appointment_service

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.get("", response_model=List[AppointmentResponse])
def list_appointments(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    date: Optional[date] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    client_id: Optional[int] = Query(default=None),
    status: Optional[AppointmentStatus] = Query(default=None),
) -> List[AppointmentResponse]:
    appointments = appointment_service.list_appointments(
        db,
        current_user.id,
        skip=skip,
        limit=limit,
        date_filter=date,
        start_date=start_date,
        end_date=end_date,
        client_id=client_id,
        status=status,
    )
    return [AppointmentResponse.model_validate(a) for a in appointments]


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    data: AppointmentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> AppointmentResponse:
    appointment = appointment_service.create_appointment(db, current_user.id, data)
    return AppointmentResponse.model_validate(appointment)


# IMPORTANT: /today must come before /{appointment_id}
@router.get("/today", response_model=List[AppointmentResponse])
def get_today_appointments(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> List[AppointmentResponse]:
    appointments = appointment_service.get_today_appointments(db, current_user.id)
    return [AppointmentResponse.model_validate(a) for a in appointments]


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> AppointmentResponse:
    appointment = appointment_service.get_appointment(db, appointment_id, current_user.id)
    return AppointmentResponse.model_validate(appointment)


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> AppointmentResponse:
    appointment = appointment_service.update_appointment(
        db, appointment_id, current_user.id, data
    )
    return AppointmentResponse.model_validate(appointment)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    appointment_service.delete_appointment(db, appointment_id, current_user.id)
