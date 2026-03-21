"""
Food item request and response schemas.
"""

from typing import Optional

from pydantic import BaseModel, field_validator


def _validate_food_name(value: str) -> str:
    value = value.strip()
    if len(value) < 2:
        raise ValueError("Food name must be at least 2 characters long.")
    if len(value) > 150:
        raise ValueError("Food name must not exceed 150 characters.")
    if value.replace(" ", "").replace("-", "").isnumeric():
        raise ValueError("Food name cannot be purely numeric.")
    return value


class FoodCreate(BaseModel):
    name: str
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    portion_size: Optional[str] = None
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return _validate_food_name(v)

    @field_validator("calories")
    @classmethod
    def validate_calories(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            if v < 0:
                raise ValueError("calories must be >= 0.")
            if v > 99999:
                raise ValueError("calories must not exceed 99999.")
        return v

    @field_validator("protein", "carbs", "fat")
    @classmethod
    def validate_macros(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            if v < 0:
                raise ValueError("Nutritional value must be >= 0.")
            if v > 9999:
                raise ValueError("Nutritional value must not exceed 9999.")
        return v

    @field_validator("portion_size")
    @classmethod
    def validate_portion_size(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 50:
                raise ValueError("portion_size must not exceed 50 characters.")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 2000:
                raise ValueError("Description must not exceed 2000 characters.")
        return v


class FoodUpdate(BaseModel):
    name: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    portion_size: Optional[str] = None
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _validate_food_name(v)

    @field_validator("calories")
    @classmethod
    def validate_calories(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            if v < 0:
                raise ValueError("calories must be >= 0.")
            if v > 99999:
                raise ValueError("calories must not exceed 99999.")
        return v

    @field_validator("protein", "carbs", "fat")
    @classmethod
    def validate_macros(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            if v < 0:
                raise ValueError("Nutritional value must be >= 0.")
            if v > 9999:
                raise ValueError("Nutritional value must not exceed 9999.")
        return v

    @field_validator("portion_size")
    @classmethod
    def validate_portion_size(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 50:
                raise ValueError("portion_size must not exceed 50 characters.")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 2000:
                raise ValueError("Description must not exceed 2000 characters.")
        return v


class FoodResponse(BaseModel):
    id: int
    name: str
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    portion_size: Optional[str] = None
    description: Optional[str] = None

    model_config = {"from_attributes": True}
