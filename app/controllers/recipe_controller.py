"""
Recipe management endpoints.
"""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.recipe import (
    RecipeCreate,
    RecipeDetailResponse,
    RecipeFoodEntry,
    RecipeFoodResponse,
    RecipeResponse,
    RecipeUpdate,
)
from app.services import recipe_service

router = APIRouter(prefix="/recipes", tags=["Recipes"])


def _build_recipe_food_response(rf) -> RecipeFoodResponse:
    food = rf.food
    return RecipeFoodResponse(
        food_id=rf.food_id,
        food_name=food.name if food else "",
        quantity_g=float(rf.quantity_g),
    )


def _build_detail(recipe) -> RecipeDetailResponse:
    base = RecipeResponse.model_validate(recipe)
    ingredients = [_build_recipe_food_response(rf) for rf in recipe.recipe_foods]
    return RecipeDetailResponse(**base.model_dump(), ingredients=ingredients)


@router.get("", response_model=List[RecipeResponse])
def list_recipes(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
) -> List[RecipeResponse]:
    recipes = recipe_service.list_recipes(db, skip=skip, limit=limit, search=search)
    return [RecipeResponse.model_validate(r) for r in recipes]


@router.post("", response_model=RecipeDetailResponse, status_code=status.HTTP_201_CREATED)
def create_recipe(
    data: RecipeCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> RecipeDetailResponse:
    recipe = recipe_service.create_recipe(db, data)
    return _build_detail(recipe)


@router.get("/{recipe_id}", response_model=RecipeDetailResponse)
def get_recipe(
    recipe_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> RecipeDetailResponse:
    recipe = recipe_service.get_recipe_detail(db, recipe_id)
    return _build_detail(recipe)


@router.put("/{recipe_id}", response_model=RecipeDetailResponse)
def update_recipe(
    recipe_id: int,
    data: RecipeUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> RecipeDetailResponse:
    recipe = recipe_service.update_recipe(db, recipe_id, data)
    return _build_detail(recipe)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    recipe_service.delete_recipe(db, recipe_id)


@router.post(
    "/{recipe_id}/foods",
    response_model=RecipeFoodResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_food_to_recipe(
    recipe_id: int,
    data: RecipeFoodEntry,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> RecipeFoodResponse:
    rf = recipe_service.add_food_to_recipe(db, recipe_id, data)
    return _build_recipe_food_response(rf)


@router.delete(
    "/{recipe_id}/foods/{food_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_food_from_recipe(
    recipe_id: int,
    food_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    recipe_service.remove_food_from_recipe(db, recipe_id, food_id)
