"""
Meal management endpoints.

Routes follow two patterns:
  - /diet-plans/{plan_id}/meals  (nested under diet plans)
  - /meals/{meal_id}             (direct meal access)
"""

from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.meal import (
    MealCreate,
    MealDetailResponse,
    MealFoodEntry,
    MealFoodResponse,
    MealUpdate,
)
from app.services import meal_service

router = APIRouter(tags=["Meals"])


def _meal_to_detail(meal) -> MealDetailResponse:
    """Convert a Meal ORM object to MealDetailResponse with enriched food data."""
    foods_out = []
    for mf in meal.meal_foods:
        food = mf.food
        foods_out.append(
            MealFoodResponse(
                food_id=mf.food_id,
                food_name=food.name if food else "",
                quantity_g=float(mf.quantity_g),
                calories=float(food.calories) if food and food.calories else None,
                protein=float(food.protein) if food and food.protein else None,
                carbs=float(food.carbs) if food and food.carbs else None,
                fat=float(food.fat) if food and food.fat else None,
            )
        )
    detail = MealDetailResponse.model_validate(meal)
    detail.foods = foods_out
    return detail


@router.get("/diet-plans/{plan_id}/meals", response_model=List[MealDetailResponse])
def list_meals(
    plan_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> List[MealDetailResponse]:
    meals = meal_service.list_meals(db, plan_id, current_user.id)
    return [_meal_to_detail(m) for m in meals]


@router.post(
    "/diet-plans/{plan_id}/meals",
    response_model=MealDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_meal(
    plan_id: int,
    data: MealCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MealDetailResponse:
    meal = meal_service.create_meal(db, plan_id, current_user.id, data)
    return _meal_to_detail(meal)


@router.put("/meals/{meal_id}", response_model=MealDetailResponse)
def update_meal(
    meal_id: int,
    data: MealUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MealDetailResponse:
    meal = meal_service.update_meal(db, meal_id, current_user.id, data)
    return _meal_to_detail(meal)


@router.delete("/meals/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal(
    meal_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    meal_service.delete_meal(db, meal_id, current_user.id)


@router.post(
    "/meals/{meal_id}/foods",
    response_model=MealFoodResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_food_to_meal(
    meal_id: int,
    data: MealFoodEntry,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MealFoodResponse:
    meal_food = meal_service.add_food_to_meal(db, meal_id, current_user.id, data)
    food = meal_food.food
    return MealFoodResponse(
        food_id=meal_food.food_id,
        food_name=food.name if food else "",
        quantity_g=float(meal_food.quantity_g),
        calories=float(food.calories) if food and food.calories else None,
        protein=float(food.protein) if food and food.protein else None,
        carbs=float(food.carbs) if food and food.carbs else None,
        fat=float(food.fat) if food and food.fat else None,
    )


@router.delete("/meals/{meal_id}/foods/{food_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_food_from_meal(
    meal_id: int,
    food_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    meal_service.remove_food_from_meal(db, meal_id, food_id, current_user.id)
