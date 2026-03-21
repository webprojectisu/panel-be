"""
Measurement request and response schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class MeasurementCreate(BaseModel):
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    bmi: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    waist_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    recorded_at: Optional[datetime] = None
    notes: Optional[str] = None

    @field_validator("height_cm")
    @classmethod
    def validate_height(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (50.0 <= v <= 300.0):
            raise ValueError("height_cm must be between 50.0 and 300.0 cm.")
        return v

    @field_validator("weight_kg")
    @classmethod
    def validate_weight(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (1.0 <= v <= 500.0):
            raise ValueError("weight_kg must be between 1.0 and 500.0 kg.")
        return v

    @field_validator("bmi")
    @classmethod
    def validate_bmi(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (5.0 <= v <= 100.0):
            raise ValueError("bmi must be between 5.0 and 100.0.")
        return v

    @field_validator("body_fat_percentage")
    @classmethod
    def validate_body_fat(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0.0 <= v <= 100.0):
            raise ValueError("body_fat_percentage must be between 0.0 and 100.0.")
        return v

    @field_validator("waist_cm")
    @classmethod
    def validate_waist(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (10.0 <= v <= 300.0):
            raise ValueError("waist_cm must be between 10.0 and 300.0 cm.")
        return v

    @field_validator("hip_cm")
    @classmethod
    def validate_hip(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (10.0 <= v <= 300.0):
            raise ValueError("hip_cm must be between 10.0 and 300.0 cm.")
        return v

    @field_validator("chest_cm")
    @classmethod
    def validate_chest(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (10.0 <= v <= 300.0):
            raise ValueError("chest_cm must be between 10.0 and 300.0 cm.")
        return v

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 2000:
                raise ValueError("Notes must not exceed 2000 characters.")
        return v


class MeasurementResponse(BaseModel):
    id: int
    client_id: int
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    bmi: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    waist_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    recorded_at: datetime
    notes: Optional[str] = None

    model_config = {"from_attributes": True}
