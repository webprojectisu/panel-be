"""
Meal management service.
"""

from typing import List

from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.associations import MealFood
from app.models.diet_plan import DietPlan
from app.models.food import Food
from app.models.meal import Meal
from app.schemas.meal import MealCreate, MealFoodEntry, MealUpdate


def _get_plan_verified(db: Session, plan_id: int, dietitian_id: int) -> DietPlan:
    """Fetch a diet plan and verify it belongs to the dietitian."""
    plan: DietPlan | None = db.get(DietPlan, plan_id)
    if plan is None:
        raise NotFoundException(f"Diet plan with id={plan_id} not found.")
    if plan.dietitian_id != dietitian_id:
        raise ForbiddenException("You do not have access to this diet plan.")
    return plan


def _get_meal_verified(db: Session, meal_id: int, dietitian_id: int) -> Meal:
    """Fetch a meal and verify its parent plan belongs to the dietitian."""
    meal: Meal | None = db.get(Meal, meal_id)
    if meal is None:
        raise NotFoundException(f"Meal with id={meal_id} not found.")
    _get_plan_verified(db, meal.diet_plan_id, dietitian_id)
    return meal


def _build_meal_detail(db: Session, meal: Meal) -> Meal:
    """Eagerly load meal_foods with food for a meal detail response."""
    db.refresh(meal)
    # Ensure meal_foods are loaded
    _ = meal.meal_foods
    for mf in meal.meal_foods:
        _ = mf.food
    return meal


def list_meals(db: Session, plan_id: int, dietitian_id: int) -> List[Meal]:
    try:
        _get_plan_verified(db, plan_id, dietitian_id)
        meals = (
            db.query(Meal)
            .options(joinedload(Meal.meal_foods).joinedload(MealFood.food))
            .filter(Meal.diet_plan_id == plan_id)
            .order_by(Meal.scheduled_time)
            .all()
        )
        return meals
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        raise exc


def create_meal(
    db: Session, plan_id: int, dietitian_id: int, data: MealCreate
) -> Meal:
    try:
        _get_plan_verified(db, plan_id, dietitian_id)
        meal = Meal(
            diet_plan_id=plan_id,
            name=data.name,
            meal_type=data.meal_type,
            scheduled_time=data.scheduled_time,
            notes=data.notes,
        )
        db.add(meal)
        db.commit()
        db.refresh(meal)
        return _build_meal_detail(db, meal)
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def update_meal(
    db: Session, meal_id: int, dietitian_id: int, data: MealUpdate
) -> Meal:
    try:
        meal = _get_meal_verified(db, meal_id, dietitian_id)
        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(meal, field, value)
        db.commit()
        db.refresh(meal)
        return _build_meal_detail(db, meal)
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def delete_meal(db: Session, meal_id: int, dietitian_id: int) -> None:
    try:
        meal = _get_meal_verified(db, meal_id, dietitian_id)
        db.delete(meal)
        db.commit()
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def add_food_to_meal(
    db: Session, meal_id: int, dietitian_id: int, data: MealFoodEntry
) -> MealFood:
    """
    Add (or update the quantity of) a food item in a meal.

    Uses upsert logic: if the food is already in the meal, update its quantity.
    """
    try:
        meal = _get_meal_verified(db, meal_id, dietitian_id)

        food: Food | None = db.get(Food, data.food_id)
        if food is None:
            raise NotFoundException(f"Food with id={data.food_id} not found.")

        existing: MealFood | None = (
            db.query(MealFood)
            .filter(MealFood.meal_id == meal_id, MealFood.food_id == data.food_id)
            .first()
        )
        if existing is not None:
            existing.quantity_g = data.quantity_g
            db.commit()
            db.refresh(existing)
            return existing

        meal_food = MealFood(
            meal_id=meal_id,
            food_id=data.food_id,
            quantity_g=data.quantity_g,
        )
        db.add(meal_food)
        db.commit()
        db.refresh(meal_food)
        return meal_food
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def remove_food_from_meal(
    db: Session, meal_id: int, food_id: int, dietitian_id: int
) -> None:
    try:
        _get_meal_verified(db, meal_id, dietitian_id)
        meal_food: MealFood | None = (
            db.query(MealFood)
            .filter(MealFood.meal_id == meal_id, MealFood.food_id == food_id)
            .first()
        )
        if meal_food is None:
            raise NotFoundException(
                f"Food with id={food_id} is not in meal with id={meal_id}."
            )
        db.delete(meal_food)
        db.commit()
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc
