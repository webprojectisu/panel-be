"""
Meal request and response schemas.
"""

from datetime import datetime, time
from typing import List, Optional

from pydantic import BaseModel, field_validator

from app.models.meal import MealType


class MealCreate(BaseModel):
    name: str
    meal_type: MealType
    scheduled_time: Optional[time] = None
    notes: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Meal name must be at least 2 characters long.")
        if len(v) > 150:
            raise ValueError("Meal name must not exceed 150 characters.")
        if v.replace(" ", "").replace("-", "").isnumeric():
            raise ValueError("Meal name cannot be purely numeric.")
        return v

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 2000:
                raise ValueError("Notes must not exceed 2000 characters.")
        return v


class MealUpdate(BaseModel):
    name: Optional[str] = None
    meal_type: Optional[MealType] = None
    scheduled_time: Optional[time] = None
    notes: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Meal name must be at least 2 characters long.")
        if len(v) > 150:
            raise ValueError("Meal name must not exceed 150 characters.")
        if v.replace(" ", "").replace("-", "").isnumeric():
            raise ValueError("Meal name cannot be purely numeric.")
        return v

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 2000:
                raise ValueError("Notes must not exceed 2000 characters.")
        return v


class MealFoodEntry(BaseModel):
    """Used when adding a food item to a meal."""

    food_id: int
    quantity_g: float

    @field_validator("quantity_g")
    @classmethod
    def validate_quantity(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("quantity_g must be greater than 0.")
        if v > 10000:
            raise ValueError("quantity_g must not exceed 10000 g.")
        return v


class MealFoodResponse(BaseModel):
    food_id: int
    food_name: str
    quantity_g: float
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None

    model_config = {"from_attributes": True}


class MealResponse(BaseModel):
    id: int
    diet_plan_id: int
    name: str
    meal_type: MealType
    scheduled_time: Optional[time] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MealDetailResponse(MealResponse):
    foods: List[MealFoodResponse] = []
