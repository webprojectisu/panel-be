"""
Payment management endpoints.

IMPORTANT: /summary must be registered BEFORE /{payment_id} to avoid
FastAPI treating "summary" as an integer path parameter.
"""

from datetime import date
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.payment import PaymentMethod, PaymentStatus
from app.models.user import User
from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentSummaryResponse,
    PaymentUpdate,
)
from app.services import payment_service

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("", response_model=List[PaymentResponse])
def list_payments(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    client_id: Optional[int] = Query(default=None),
    status: Optional[PaymentStatus] = Query(default=None),
    payment_method: Optional[PaymentMethod] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
) -> List[PaymentResponse]:
    payments = payment_service.list_payments(
        db,
        current_user.id,
        skip=skip,
        limit=limit,
        client_id=client_id,
        status=status,
        payment_method=payment_method,
        start_date=start_date,
        end_date=end_date,
    )
    return [PaymentResponse.model_validate(p) for p in payments]


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    data: PaymentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PaymentResponse:
    payment = payment_service.create_payment(db, current_user.id, data)
    return PaymentResponse.model_validate(payment)


# IMPORTANT: /summary must come before /{payment_id}
@router.get("/summary", response_model=PaymentSummaryResponse)
def get_payment_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    period: str = Query(default="monthly"),
    date: Optional[str] = Query(default=None, description="Reference month YYYY-MM"),
) -> PaymentSummaryResponse:
    summary = payment_service.get_payment_summary(
        db, current_user.id, period=period, date_str=date
    )
    return PaymentSummaryResponse(**summary)


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PaymentResponse:
    payment = payment_service.get_payment(db, payment_id, current_user.id)
    return PaymentResponse.model_validate(payment)


@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: int,
    data: PaymentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PaymentResponse:
    payment = payment_service.update_payment(db, payment_id, current_user.id, data)
    return PaymentResponse.model_validate(payment)


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(
    payment_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    payment_service.delete_payment(db, payment_id, current_user.id)
