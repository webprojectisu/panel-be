"""
Body measurement endpoints.

Routes are nested under /clients/{client_id}/measurements, plus a
standalone /measurements/{measurement_id} for delete.
"""

from typing import Annotated, List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.measurement import MeasurementCreate, MeasurementResponse
from app.services import measurement_service

router = APIRouter(tags=["Measurements"])


@router.get(
    "/clients/{client_id}/measurements",
    response_model=List[MeasurementResponse],
)
def list_measurements(
    client_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> List[MeasurementResponse]:
    measurements = measurement_service.list_measurements(
        db, client_id, current_user.id, skip=skip, limit=limit
    )
    return [MeasurementResponse.model_validate(m) for m in measurements]


@router.post(
    "/clients/{client_id}/measurements",
    response_model=MeasurementResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_measurement(
    client_id: int,
    data: MeasurementCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MeasurementResponse:
    measurement = measurement_service.create_measurement(
        db, client_id, current_user.id, data
    )
    return MeasurementResponse.model_validate(measurement)


# IMPORTANT: /latest must be registered before /{measurement_id} in main.py
# but since this router has no /{measurement_id} GET, there's no conflict here.
@router.get(
    "/clients/{client_id}/measurements/latest",
    response_model=MeasurementResponse,
)
def get_latest_measurement(
    client_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MeasurementResponse:
    from app.core.exceptions import NotFoundException

    measurement = measurement_service.get_latest_measurement(
        db, client_id, current_user.id
    )
    if measurement is None:
        raise NotFoundException("No measurements found for this client.")
    return MeasurementResponse.model_validate(measurement)


@router.delete(
    "/measurements/{measurement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_measurement(
    measurement_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    measurement_service.delete_measurement(db, measurement_id, current_user.id)
