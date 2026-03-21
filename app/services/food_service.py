"""
Food item management service.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, ConflictException, NotFoundException
from app.models.associations import MealFood, RecipeFood
from app.models.food import Food
from app.schemas.food import FoodCreate, FoodUpdate


def list_foods(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
) -> List[Food]:
    try:
        query = db.query(Food)
        if search:
            query = query.filter(Food.name.ilike(f"%{search}%"))
        return query.order_by(Food.name).offset(skip).limit(limit).all()
    except Exception as exc:
        raise exc


def create_food(db: Session, data: FoodCreate) -> Food:
    """Create a food item. Raises ConflictException if the name already exists (case-insensitive)."""
    try:
        existing = (
            db.query(Food).filter(Food.name.ilike(data.name)).first()
        )
        if existing is not None:
            raise ConflictException(
                f"A food item named '{data.name}' already exists."
            )
        food = Food(
            name=data.name,
            calories=data.calories,
            protein=data.protein,
            carbs=data.carbs,
            fat=data.fat,
            portion_size=data.portion_size,
            description=data.description,
        )
        db.add(food)
        db.commit()
        db.refresh(food)
        return food
    except ConflictException:
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def get_food(db: Session, food_id: int) -> Food:
    try:
        food: Food | None = db.get(Food, food_id)
        if food is None:
            raise NotFoundException(f"Food with id={food_id} not found.")
        return food
    except NotFoundException:
        raise
    except Exception as exc:
        raise exc


def update_food(db: Session, food_id: int, data: FoodUpdate) -> Food:
    try:
        food = get_food(db, food_id)
        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(food, field, value)
        db.commit()
        db.refresh(food)
        return food
    except NotFoundException:
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def delete_food(db: Session, food_id: int) -> None:
    """
    Delete a food item.

    Raises BadRequestException if the food is referenced by any meal or recipe
    (to preserve referential integrity at the application layer).
    """
    try:
        food = get_food(db, food_id)

        in_meal = db.query(MealFood).filter(MealFood.food_id == food_id).first()
        if in_meal is not None:
            raise BadRequestException(
                "Food is in use by one or more meals and cannot be deleted."
            )

        in_recipe = db.query(RecipeFood).filter(RecipeFood.food_id == food_id).first()
        if in_recipe is not None:
            raise BadRequestException(
                "Food is in use by one or more recipes and cannot be deleted."
            )

        db.delete(food)
        db.commit()
    except (NotFoundException, BadRequestException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc
