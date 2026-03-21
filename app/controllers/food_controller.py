"""
Food item management endpoints.
"""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.food import FoodCreate, FoodResponse, FoodUpdate
from app.services import food_service

router = APIRouter(prefix="/foods", tags=["Foods"])


@router.get("", response_model=List[FoodResponse])
def list_foods(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
) -> List[FoodResponse]:
    foods = food_service.list_foods(db, skip=skip, limit=limit, search=search)
    return [FoodResponse.model_validate(f) for f in foods]


@router.post("", response_model=FoodResponse, status_code=status.HTTP_201_CREATED)
def create_food(
    data: FoodCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> FoodResponse:
    food = food_service.create_food(db, data)
    return FoodResponse.model_validate(food)


@router.get("/{food_id}", response_model=FoodResponse)
def get_food(
    food_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> FoodResponse:
    food = food_service.get_food(db, food_id)
    return FoodResponse.model_validate(food)


@router.put("/{food_id}", response_model=FoodResponse)
def update_food(
    food_id: int,
    data: FoodUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> FoodResponse:
    food = food_service.update_food(db, food_id, data)
    return FoodResponse.model_validate(food)


@router.delete("/{food_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food(
    food_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    food_service.delete_food(db, food_id)
