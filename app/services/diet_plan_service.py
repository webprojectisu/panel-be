"""
Diet plan management service.
"""

from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.associations import diet_plan_recipe
from app.models.client import Client
from app.models.diet_plan import DietPlan, DietPlanStatus
from app.models.recipe import Recipe
from app.schemas.diet_plan import DietPlanCreate, DietPlanUpdate


def _enrich(plan: DietPlan) -> DietPlan:
    """Attach client_name as a transient attribute."""
    if plan.client:
        plan.__dict__["client_name"] = plan.client.full_name
    else:
        plan.__dict__["client_name"] = None
    return plan


def list_diet_plans(
    db: Session,
    dietitian_id: int,
    skip: int = 0,
    limit: int = 20,
    client_id: Optional[int] = None,
    status: Optional[DietPlanStatus] = None,
) -> List[DietPlan]:
    try:
        query = db.query(DietPlan).filter(DietPlan.dietitian_id == dietitian_id)
        if client_id is not None:
            query = query.filter(DietPlan.client_id == client_id)
        if status is not None:
            query = query.filter(DietPlan.status == status)
        plans = (
            query.order_by(DietPlan.created_at.desc()).offset(skip).limit(limit).all()
        )
        return [_enrich(p) for p in plans]
    except Exception as exc:
        raise exc


def create_diet_plan(
    db: Session, dietitian_id: int, data: DietPlanCreate
) -> DietPlan:
    try:
        # Verify client belongs to this dietitian
        client: Client | None = db.get(Client, data.client_id)
        if client is None:
            raise NotFoundException(f"Client with id={data.client_id} not found.")
        if client.dietitian_id != dietitian_id:
            raise ForbiddenException("You do not have access to this client.")

        plan = DietPlan(
            client_id=data.client_id,
            dietitian_id=dietitian_id,
            title=data.title,
            description=data.description,
            start_date=data.start_date,
            end_date=data.end_date,
            status=data.status,
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return _enrich(plan)
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def get_diet_plan(
    db: Session, plan_id: int, dietitian_id: int
) -> DietPlan:
    try:
        plan: DietPlan | None = db.get(DietPlan, plan_id)
        if plan is None:
            raise NotFoundException(f"Diet plan with id={plan_id} not found.")
        if plan.dietitian_id != dietitian_id:
            raise ForbiddenException("You do not have access to this diet plan.")
        return _enrich(plan)
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        raise exc


def get_diet_plan_detail(
    db: Session, plan_id: int, dietitian_id: int
) -> DietPlan:
    """Load diet plan with nested meals, meal foods, and recipes."""
    try:
        plan = (
            db.query(DietPlan)
            .options(
                joinedload(DietPlan.meals).joinedload("meal_foods").joinedload("food"),
                joinedload(DietPlan.recipes).joinedload("recipe_foods").joinedload("food"),
                joinedload(DietPlan.client),
            )
            .filter(DietPlan.id == plan_id)
            .first()
        )
        if plan is None:
            raise NotFoundException(f"Diet plan with id={plan_id} not found.")
        if plan.dietitian_id != dietitian_id:
            raise ForbiddenException("You do not have access to this diet plan.")
        return _enrich(plan)
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        raise exc


def update_diet_plan(
    db: Session, plan_id: int, dietitian_id: int, data: DietPlanUpdate
) -> DietPlan:
    try:
        plan = get_diet_plan(db, plan_id, dietitian_id)
        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(plan, field, value)
        db.commit()
        db.refresh(plan)
        return _enrich(plan)
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def delete_diet_plan(
    db: Session, plan_id: int, dietitian_id: int
) -> None:
    try:
        plan = get_diet_plan(db, plan_id, dietitian_id)
        db.delete(plan)
        db.commit()
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def add_recipe_to_plan(
    db: Session, plan_id: int, recipe_id: int, dietitian_id: int
) -> None:
    try:
        plan = get_diet_plan(db, plan_id, dietitian_id)
        recipe: Recipe | None = db.get(Recipe, recipe_id)
        if recipe is None:
            raise NotFoundException(f"Recipe with id={recipe_id} not found.")
        # Avoid duplicates
        if recipe not in plan.recipes:
            plan.recipes.append(recipe)
            db.commit()
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def remove_recipe_from_plan(
    db: Session, plan_id: int, recipe_id: int, dietitian_id: int
) -> None:
    try:
        plan = get_diet_plan(db, plan_id, dietitian_id)
        recipe: Recipe | None = db.get(Recipe, recipe_id)
        if recipe is None:
            raise NotFoundException(f"Recipe with id={recipe_id} not found.")
        if recipe in plan.recipes:
            plan.recipes.remove(recipe)
            db.commit()
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc
