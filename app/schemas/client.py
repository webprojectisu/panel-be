"""
Client request and response schemas.
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.models.client import Gender
from app.schemas.auth import _validate_full_name, _validate_phone
from app.schemas.appointment import AppointmentResponse
from app.schemas.diet_plan import DietPlanResponse
from app.schemas.measurement import MeasurementResponse

_DATE_MIN = date(1900, 1, 1)


def _validate_date_of_birth(v: Optional[date]) -> Optional[date]:
    if v is None:
        return v
    today = date.today()
    if v > today:
        raise ValueError("date_of_birth cannot be in the future.")
    if v < _DATE_MIN:
        raise ValueError("date_of_birth cannot be before 1900-01-01.")
    return v


class ClientCreate(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    notes: Optional[str] = None

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        return _validate_full_name(v)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return v.strip().lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _validate_phone(v)

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: Optional[date]) -> Optional[date]:
        return _validate_date_of_birth(v)

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 2000:
                raise ValueError("Notes must not exceed 2000 characters.")
        return v


class ClientUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    notes: Optional[str] = None

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _validate_full_name(v)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return v.strip().lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _validate_phone(v)

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: Optional[date]) -> Optional[date]:
        return _validate_date_of_birth(v)

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 2000:
                raise ValueError("Notes must not exceed 2000 characters.")
        return v


class ClientResponse(BaseModel):
    id: int
    dietitian_id: int
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ClientSummaryResponse(BaseModel):
    client: ClientResponse
    latest_measurement: Optional[MeasurementResponse] = None
    active_diet_plan: Optional[DietPlanResponse] = None
    upcoming_appointments: List[AppointmentResponse] = []
    payment_balance: float = 0.0
