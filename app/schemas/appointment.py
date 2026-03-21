"""
Appointment request and response schemas.
"""

from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator

from app.models.appointment import AppointmentStatus


class AppointmentCreate(BaseModel):
    client_id: int
    appointment_date: date
    start_time: time
    end_time: Optional[time] = None
    notes: Optional[str] = None

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 2000:
                raise ValueError("Notes must not exceed 2000 characters.")
        return v

    @model_validator(mode="after")
    def validate_time_range(self) -> "AppointmentCreate":
        if self.end_time is not None and self.start_time is not None:
            if self.end_time <= self.start_time:
                raise ValueError("end_time must be after start_time.")
        return self


class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 2000:
                raise ValueError("Notes must not exceed 2000 characters.")
        return v

    @model_validator(mode="after")
    def validate_time_range(self) -> "AppointmentUpdate":
        if self.end_time is not None and self.start_time is not None:
            if self.end_time <= self.start_time:
                raise ValueError("end_time must be after start_time.")
        return self


class AppointmentResponse(BaseModel):
    id: int
    client_id: int
    dietitian_id: int
    appointment_date: date
    start_time: time
    end_time: Optional[time] = None
    status: AppointmentStatus
    notes: Optional[str] = None
    created_at: datetime
    client_name: Optional[str] = None

    model_config = {"from_attributes": True}
