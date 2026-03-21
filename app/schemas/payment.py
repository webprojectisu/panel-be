"""
Payment request and response schemas.
"""

import re
from datetime import date, datetime
from decimal import Decimal, ROUND_DOWN
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator

from app.models.payment import PaymentMethod, PaymentStatus

# Standard 3-letter ISO 4217 currency codes (a non-exhaustive but common set)
_ISO_4217_PATTERN = re.compile(r"^[A-Z]{3}$")


class PaymentCreate(BaseModel):
    client_id: int
    amount: Decimal
    currency: str = "TRY"
    payment_date: date
    payment_method: PaymentMethod
    status: PaymentStatus = PaymentStatus.pending
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("amount must be greater than 0.")
        # Ensure at most 2 decimal places
        quantized = v.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        if quantized != v:
            raise ValueError("amount must have at most 2 decimal places.")
        return v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        v = v.strip().upper()
        if not _ISO_4217_PATTERN.match(v):
            raise ValueError(
                "currency must be a valid 3-letter ISO 4217 code (e.g. TRY, USD, EUR)."
            )
        return v

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 2000:
                raise ValueError("Notes must not exceed 2000 characters.")
        return v


class PaymentUpdate(BaseModel):
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    payment_date: Optional[date] = None
    payment_method: Optional[PaymentMethod] = None
    status: Optional[PaymentStatus] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is None:
            return v
        if v <= 0:
            raise ValueError("amount must be greater than 0.")
        quantized = v.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        if quantized != v:
            raise ValueError("amount must have at most 2 decimal places.")
        return v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().upper()
        if not _ISO_4217_PATTERN.match(v):
            raise ValueError(
                "currency must be a valid 3-letter ISO 4217 code (e.g. TRY, USD, EUR)."
            )
        return v

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 2000:
                raise ValueError("Notes must not exceed 2000 characters.")
        return v


class PaymentResponse(BaseModel):
    id: int
    client_id: int
    dietitian_id: int
    amount: Decimal
    currency: str
    payment_date: date
    payment_method: PaymentMethod
    status: PaymentStatus
    notes: Optional[str] = None
    created_at: datetime
    client_name: Optional[str] = None

    model_config = {"from_attributes": True}


class PaymentSummaryResponse(BaseModel):
    total_income: float
    currency: str
    period: str
    breakdown_by_method: Dict[str, float]
    monthly_trend: List[Dict[str, Any]]
