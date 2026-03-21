"""
Payment management service.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.client import Client
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.schemas.payment import PaymentCreate, PaymentUpdate


def _enrich(payment: Payment) -> Payment:
    if payment.client:
        payment.__dict__["client_name"] = payment.client.full_name
    else:
        payment.__dict__["client_name"] = None
    return payment


def _verify_client(db: Session, client_id: int, dietitian_id: int) -> Client:
    client: Client | None = db.get(Client, client_id)
    if client is None:
        raise NotFoundException(f"Client with id={client_id} not found.")
    if client.dietitian_id != dietitian_id:
        raise ForbiddenException("You do not have access to this client.")
    return client


def list_payments(
    db: Session,
    dietitian_id: int,
    skip: int = 0,
    limit: int = 20,
    client_id: Optional[int] = None,
    status: Optional[PaymentStatus] = None,
    payment_method: Optional[PaymentMethod] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[Payment]:
    try:
        query = db.query(Payment).filter(Payment.dietitian_id == dietitian_id)
        if client_id is not None:
            query = query.filter(Payment.client_id == client_id)
        if status is not None:
            query = query.filter(Payment.status == status)
        if payment_method is not None:
            query = query.filter(Payment.payment_method == payment_method)
        if start_date is not None:
            query = query.filter(Payment.payment_date >= start_date)
        if end_date is not None:
            query = query.filter(Payment.payment_date <= end_date)
        payments = (
            query.order_by(Payment.payment_date.desc()).offset(skip).limit(limit).all()
        )
        return [_enrich(p) for p in payments]
    except Exception as exc:
        raise exc


def create_payment(db: Session, dietitian_id: int, data: PaymentCreate) -> Payment:
    try:
        _verify_client(db, data.client_id, dietitian_id)
        payment = Payment(
            client_id=data.client_id,
            dietitian_id=dietitian_id,
            amount=data.amount,
            currency=data.currency,
            payment_date=data.payment_date,
            payment_method=data.payment_method,
            status=data.status,
            notes=data.notes,
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return _enrich(payment)
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def get_payment(db: Session, payment_id: int, dietitian_id: int) -> Payment:
    try:
        payment: Payment | None = db.get(Payment, payment_id)
        if payment is None:
            raise NotFoundException(f"Payment with id={payment_id} not found.")
        if payment.dietitian_id != dietitian_id:
            raise ForbiddenException("You do not have access to this payment.")
        return _enrich(payment)
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        raise exc


def update_payment(
    db: Session, payment_id: int, dietitian_id: int, data: PaymentUpdate
) -> Payment:
    try:
        payment = get_payment(db, payment_id, dietitian_id)
        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(payment, field, value)
        db.commit()
        db.refresh(payment)
        return _enrich(payment)
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def delete_payment(db: Session, payment_id: int, dietitian_id: int) -> None:
    try:
        payment = get_payment(db, payment_id, dietitian_id)
        db.delete(payment)
        db.commit()
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def get_payment_summary(
    db: Session,
    dietitian_id: int,
    period: str = "monthly",
    date_str: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compute payment summary statistics for the dietitian.

    period="monthly" → aggregate for current calendar month.
    date_str → optional YYYY-MM string to override the reference month.
    """
    try:
        today = date.today()
        if date_str:
            ref = datetime.strptime(date_str, "%Y-%m").date()
        else:
            ref = today

        ref_year, ref_month = ref.year, ref.month

        # Base query: completed payments for this dietitian
        base_q = db.query(Payment).filter(
            Payment.dietitian_id == dietitian_id,
            Payment.status == PaymentStatus.completed,
        )

        # Total income for the reference month
        total_result = (
            base_q.filter(
                extract("year", Payment.payment_date) == ref_year,
                extract("month", Payment.payment_date) == ref_month,
            )
            .with_entities(func.sum(Payment.amount))
            .scalar()
        )
        total_income = float(total_result) if total_result else 0.0

        # Determine currency (most used)
        currency_result = (
            db.query(Payment.currency, func.count(Payment.id).label("cnt"))
            .filter(Payment.dietitian_id == dietitian_id)
            .group_by(Payment.currency)
            .order_by(func.count(Payment.id).desc())
            .first()
        )
        currency = currency_result[0] if currency_result else "TRY"

        # Breakdown by payment method for the reference month
        method_rows = (
            base_q.filter(
                extract("year", Payment.payment_date) == ref_year,
                extract("month", Payment.payment_date) == ref_month,
            )
            .with_entities(Payment.payment_method, func.sum(Payment.amount))
            .group_by(Payment.payment_method)
            .all()
        )
        breakdown_by_method: Dict[str, float] = {
            method.value: float(total) for method, total in method_rows
        }

        # Monthly trend: last 6 months
        monthly_trend: List[Dict[str, Any]] = []
        for i in range(5, -1, -1):
            # Calculate month offset
            month_offset = ref_month - i
            year_offset = ref_year
            while month_offset <= 0:
                month_offset += 12
                year_offset -= 1

            month_total = (
                base_q.filter(
                    extract("year", Payment.payment_date) == year_offset,
                    extract("month", Payment.payment_date) == month_offset,
                )
                .with_entities(func.sum(Payment.amount))
                .scalar()
            )
            monthly_trend.append(
                {
                    "month": f"{year_offset}-{month_offset:02d}",
                    "amount": float(month_total) if month_total else 0.0,
                }
            )

        return {
            "total_income": total_income,
            "currency": currency,
            "period": f"{ref_year}-{ref_month:02d}",
            "breakdown_by_method": breakdown_by_method,
            "monthly_trend": monthly_trend,
        }
    except Exception as exc:
        raise exc
