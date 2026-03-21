"""
Recipe management service.
"""

from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import NotFoundException
from app.models.associations import RecipeFood
from app.models.food import Food
from app.models.recipe import Recipe
from app.schemas.recipe import RecipeCreate, RecipeFoodEntry, RecipeUpdate


def _build_detail(db: Session, recipe: Recipe) -> Recipe:
    """Eagerly refresh recipe_foods with food objects."""
    db.refresh(recipe)
    for rf in recipe.recipe_foods:
        _ = rf.food
    return recipe


def list_recipes(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
) -> List[Recipe]:
    try:
        query = db.query(Recipe)
        if search:
            query = query.filter(Recipe.title.ilike(f"%{search}%"))
        return query.order_by(Recipe.title).offset(skip).limit(limit).all()
    except Exception as exc:
        raise exc


def create_recipe(db: Session, data: RecipeCreate) -> Recipe:
    """Create a recipe and its ingredient (RecipeFood) entries."""
    try:
        # Validate all food_ids exist before writing anything
        if data.ingredients:
            for entry in data.ingredients:
                food: Food | None = db.get(Food, entry.food_id)
                if food is None:
                    raise NotFoundException(f"Food with id={entry.food_id} not found.")

        recipe = Recipe(
            title=data.title,
            description=data.description,
            instructions=data.instructions,
            preparation_time_minutes=data.preparation_time_minutes,
            calories=data.calories,
        )
        db.add(recipe)
        db.flush()  # assign recipe.id before creating RecipeFood rows

        if data.ingredients:
            for entry in data.ingredients:
                rf = RecipeFood(
                    recipe_id=recipe.id,
                    food_id=entry.food_id,
                    quantity_g=entry.quantity_g,
                )
                db.add(rf)

        db.commit()
        return _build_detail(db, recipe)
    except NotFoundException:
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def get_recipe(db: Session, recipe_id: int) -> Recipe:
    try:
        recipe: Recipe | None = db.get(Recipe, recipe_id)
        if recipe is None:
            raise NotFoundException(f"Recipe with id={recipe_id} not found.")
        return recipe
    except NotFoundException:
        raise
    except Exception as exc:
        raise exc


def get_recipe_detail(db: Session, recipe_id: int) -> Recipe:
    try:
        recipe = (
            db.query(Recipe)
            .options(joinedload(Recipe.recipe_foods).joinedload(RecipeFood.food))
            .filter(Recipe.id == recipe_id)
            .first()
        )
        if recipe is None:
            raise NotFoundException(f"Recipe with id={recipe_id} not found.")
        return recipe
    except NotFoundException:
        raise
    except Exception as exc:
        raise exc


def update_recipe(db: Session, recipe_id: int, data: RecipeUpdate) -> Recipe:
    try:
        recipe = get_recipe(db, recipe_id)
        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(recipe, field, value)
        db.commit()
        return _build_detail(db, recipe)
    except NotFoundException:
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def delete_recipe(db: Session, recipe_id: int) -> None:
    try:
        recipe = get_recipe(db, recipe_id)
        db.delete(recipe)
        db.commit()
    except NotFoundException:
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def add_food_to_recipe(
    db: Session, recipe_id: int, data: RecipeFoodEntry
) -> RecipeFood:
    try:
        get_recipe(db, recipe_id)  # verify existence
        food: Food | None = db.get(Food, data.food_id)
        if food is None:
            raise NotFoundException(f"Food with id={data.food_id} not found.")

        existing: RecipeFood | None = (
            db.query(RecipeFood)
            .filter(
                RecipeFood.recipe_id == recipe_id, RecipeFood.food_id == data.food_id
            )
            .first()
        )
        if existing is not None:
            existing.quantity_g = data.quantity_g
            db.commit()
            db.refresh(existing)
            return existing

        rf = RecipeFood(
            recipe_id=recipe_id,
            food_id=data.food_id,
            quantity_g=data.quantity_g,
        )
        db.add(rf)
        db.commit()
        db.refresh(rf)
        return rf
    except NotFoundException:
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def remove_food_from_recipe(
    db: Session, recipe_id: int, food_id: int
) -> None:
    try:
        get_recipe(db, recipe_id)
        rf: RecipeFood | None = (
            db.query(RecipeFood)
            .filter(RecipeFood.recipe_id == recipe_id, RecipeFood.food_id == food_id)
            .first()
        )
        if rf is None:
            raise NotFoundException(
                f"Food with id={food_id} is not in recipe with id={recipe_id}."
            )
        db.delete(rf)
        db.commit()
    except NotFoundException:
        raise
    except Exception as exc:
        db.rollback()
        raise exc
