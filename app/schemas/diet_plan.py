"""
Diet plan request and response schemas.
"""

from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, field_validator, model_validator

from app.models.diet_plan import DietPlanStatus
from app.schemas.auth import _validate_full_name

if TYPE_CHECKING:
    from app.schemas.meal import MealDetailResponse
    from app.schemas.recipe import RecipeResponse


def _validate_title(value: str) -> str:
    """Validate a plan/recipe title field."""
    value = value.strip()
    if len(value) < 2:
        raise ValueError("Title must be at least 2 characters long.")
    if len(value) > 150:
        raise ValueError("Title must not exceed 150 characters.")
    if value.replace(" ", "").replace("-", "").replace("'", "").isnumeric():
        raise ValueError("Title cannot be purely numeric.")
    return value


class DietPlanCreate(BaseModel):
    client_id: int
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: DietPlanStatus = DietPlanStatus.draft

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        return _validate_title(v)

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 2000:
                raise ValueError("Description must not exceed 2000 characters.")
        return v

    @model_validator(mode="after")
    def validate_date_range(self) -> "DietPlanCreate":
        if self.start_date is not None and self.end_date is not None:
            if self.end_date <= self.start_date:
                raise ValueError("end_date must be after start_date.")
        return self


class DietPlanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[DietPlanStatus] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _validate_title(v)

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 2000:
                raise ValueError("Description must not exceed 2000 characters.")
        return v

    @model_validator(mode="after")
    def validate_date_range(self) -> "DietPlanUpdate":
        if self.start_date is not None and self.end_date is not None:
            if self.end_date <= self.start_date:
                raise ValueError("end_date must be after start_date.")
        return self


class DietPlanResponse(BaseModel):
    id: int
    client_id: int
    dietitian_id: int
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: DietPlanStatus
    created_at: datetime
    client_name: Optional[str] = None

    model_config = {"from_attributes": True}


class DietPlanDetailResponse(DietPlanResponse):
    meals: List["MealDetailResponse"] = []
    recipes: List["RecipeResponse"] = []


# Resolve forward references after meal/recipe schemas are defined
from app.schemas.meal import MealDetailResponse  # noqa: E402
from app.schemas.recipe import RecipeResponse  # noqa: E402

DietPlanDetailResponse.model_rebuild()
