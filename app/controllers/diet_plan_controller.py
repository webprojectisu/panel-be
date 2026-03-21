"""
Diet plan management endpoints.
"""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.diet_plan import DietPlanStatus
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.diet_plan import (
    DietPlanCreate,
    DietPlanDetailResponse,
    DietPlanResponse,
    DietPlanUpdate,
)
from app.services import diet_plan_service

router = APIRouter(prefix="/diet-plans", tags=["Diet Plans"])


@router.get("", response_model=List[DietPlanResponse])
def list_diet_plans(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    client_id: Optional[int] = Query(default=None),
    status: Optional[DietPlanStatus] = Query(default=None),
) -> List[DietPlanResponse]:
    plans = diet_plan_service.list_diet_plans(
        db, current_user.id, skip=skip, limit=limit, client_id=client_id, status=status
    )
    return [DietPlanResponse.model_validate(p) for p in plans]


@router.post("", response_model=DietPlanResponse, status_code=status.HTTP_201_CREATED)
def create_diet_plan(
    data: DietPlanCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DietPlanResponse:
    plan = diet_plan_service.create_diet_plan(db, current_user.id, data)
    return DietPlanResponse.model_validate(plan)


@router.get("/{plan_id}", response_model=DietPlanDetailResponse)
def get_diet_plan(
    plan_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DietPlanDetailResponse:
    plan = diet_plan_service.get_diet_plan_detail(db, plan_id, current_user.id)
    return _build_detail_response(plan)


@router.put("/{plan_id}", response_model=DietPlanResponse)
def update_diet_plan(
    plan_id: int,
    data: DietPlanUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DietPlanResponse:
    plan = diet_plan_service.update_diet_plan(db, plan_id, current_user.id, data)
    return DietPlanResponse.model_validate(plan)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_diet_plan(
    plan_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    diet_plan_service.delete_diet_plan(db, plan_id, current_user.id)


@router.post(
    "/{plan_id}/recipes/{recipe_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
def add_recipe_to_plan(
    plan_id: int,
    recipe_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    diet_plan_service.add_recipe_to_plan(db, plan_id, recipe_id, current_user.id)
    return MessageResponse(message="Recipe added to diet plan.")


@router.delete(
    "/{plan_id}/recipes/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_recipe_from_plan(
    plan_id: int,
    recipe_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    diet_plan_service.remove_recipe_from_plan(db, plan_id, recipe_id, current_user.id)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _build_detail_response(plan) -> DietPlanDetailResponse:
    """Map a DietPlan ORM object (with eager-loaded relations) to DietPlanDetailResponse."""
    from app.schemas.meal import MealDetailResponse, MealFoodResponse
    from app.schemas.recipe import RecipeDetailResponse, RecipeFoodResponse, RecipeResponse

    meals_out = []
    for meal in plan.meals:
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
        meal_detail = MealDetailResponse.model_validate(meal)
        meal_detail.foods = foods_out
        meals_out.append(meal_detail)

    recipes_out = []
    for recipe in plan.recipes:
        recipes_out.append(RecipeResponse.model_validate(recipe))

    base = DietPlanResponse.model_validate(plan)
    return DietPlanDetailResponse(
        **base.model_dump(),
        meals=meals_out,
        recipes=recipes_out,
    )
