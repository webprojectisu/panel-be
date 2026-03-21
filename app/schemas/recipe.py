"""
Recipe request and response schemas.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator


class RecipeFoodEntry(BaseModel):
    """Ingredient entry when creating or updating a recipe."""

    food_id: int
    quantity_g: float

    @field_validator("quantity_g")
    @classmethod
    def validate_quantity(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("quantity_g must be greater than 0.")
        return v


class RecipeCreate(BaseModel):
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    preparation_time_minutes: Optional[int] = None
    calories: Optional[float] = None
    ingredients: Optional[List[RecipeFoodEntry]] = []

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Title must be at least 2 characters long.")
        if len(v) > 150:
            raise ValueError("Title must not exceed 150 characters.")
        if v.replace(" ", "").replace("-", "").replace("'", "").isnumeric():
            raise ValueError("Title cannot be purely numeric.")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 2000:
                raise ValueError("Description must not exceed 2000 characters.")
        return v

    @field_validator("instructions")
    @classmethod
    def validate_instructions(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 10000:
                raise ValueError("Instructions must not exceed 10000 characters.")
        return v

    @field_validator("preparation_time_minutes")
    @classmethod
    def validate_prep_time(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if v <= 0:
                raise ValueError("preparation_time_minutes must be greater than 0.")
            if v > 1440:
                raise ValueError("preparation_time_minutes must not exceed 1440 (24 hours).")
        return v

    @field_validator("calories")
    @classmethod
    def validate_calories(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("calories must be >= 0.")
        return v


class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    preparation_time_minutes: Optional[int] = None
    calories: Optional[float] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Title must be at least 2 characters long.")
        if len(v) > 150:
            raise ValueError("Title must not exceed 150 characters.")
        if v.replace(" ", "").replace("-", "").replace("'", "").isnumeric():
            raise ValueError("Title cannot be purely numeric.")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 2000:
                raise ValueError("Description must not exceed 2000 characters.")
        return v

    @field_validator("instructions")
    @classmethod
    def validate_instructions(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 10000:
                raise ValueError("Instructions must not exceed 10000 characters.")
        return v

    @field_validator("preparation_time_minutes")
    @classmethod
    def validate_prep_time(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if v <= 0:
                raise ValueError("preparation_time_minutes must be greater than 0.")
            if v > 1440:
                raise ValueError("preparation_time_minutes must not exceed 1440 (24 hours).")
        return v

    @field_validator("calories")
    @classmethod
    def validate_calories(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("calories must be >= 0.")
        return v


class RecipeFoodResponse(BaseModel):
    food_id: int
    food_name: str
    quantity_g: float

    model_config = {"from_attributes": True}


class RecipeResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    preparation_time_minutes: Optional[int] = None
    calories: Optional[float] = None

    model_config = {"from_attributes": True}


class RecipeDetailResponse(RecipeResponse):
    ingredients: List[RecipeFoodResponse] = []
