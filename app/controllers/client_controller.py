"""
Client management endpoints.
"""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.client import Gender
from app.models.user import User
from app.schemas.client import ClientCreate, ClientResponse, ClientSummaryResponse, ClientUpdate
from app.schemas.measurement import MeasurementResponse
from app.schemas.appointment import AppointmentResponse
from app.schemas.diet_plan import DietPlanResponse
from app.services import client_service

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.get("", response_model=List[ClientResponse])
def list_clients(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    gender: Optional[Gender] = Query(default=None),
) -> List[ClientResponse]:
    clients = client_service.list_clients(
        db, current_user.id, skip=skip, limit=limit, search=search, gender=gender
    )
    return [ClientResponse.model_validate(c) for c in clients]


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    data: ClientCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ClientResponse:
    client = client_service.create_client(db, current_user.id, data)
    return ClientResponse.model_validate(client)


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ClientResponse:
    client = client_service.get_client(db, client_id, current_user.id)
    return ClientResponse.model_validate(client)


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int,
    data: ClientUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ClientResponse:
    client = client_service.update_client(db, client_id, current_user.id, data)
    return ClientResponse.model_validate(client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    client_service.delete_client(db, client_id, current_user.id)


@router.get("/{client_id}/summary", response_model=ClientSummaryResponse)
def get_client_summary(
    client_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ClientSummaryResponse:
    summary = client_service.get_client_summary(db, client_id, current_user.id)
    return ClientSummaryResponse(
        client=ClientResponse.model_validate(summary["client"]),
        latest_measurement=(
            MeasurementResponse.model_validate(summary["latest_measurement"])
            if summary["latest_measurement"] else None
        ),
        active_diet_plan=(
            DietPlanResponse.model_validate(summary["active_diet_plan"])
            if summary["active_diet_plan"] else None
        ),
        upcoming_appointments=[
            AppointmentResponse.model_validate(a)
            for a in summary["upcoming_appointments"]
        ],
        payment_balance=summary["payment_balance"],
    )
