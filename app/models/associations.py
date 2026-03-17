"""
Association tables and models for many-to-many relationships.

- diet_plan_recipe : plain join table (no extra columns needed)
- MealFood         : association model — a food item inside a meal with a quantity
- RecipeFood       : association model — a food item inside a recipe with a quantity
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Table,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

# ---------------------------------------------------------------------------
# Plain association table: DietPlan <-> Recipe (no extra columns)
# ---------------------------------------------------------------------------

diet_plan_recipe = Table(
    "diet_plan_recipe",
    Base.metadata,
    Column(
        "diet_plan_id",
        Integer,
        ForeignKey("diet_plans.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "recipe_id",
        Integer,
        ForeignKey("recipes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


# ---------------------------------------------------------------------------
# Association model: Meal <-> Food  (with quantity)
# ---------------------------------------------------------------------------

class MealFood(Base):
    """
    Represents a food item within a specific meal, including the quantity used.
    Using a full model (not a plain Table) because quantity_g is needed.
    """

    __tablename__ = "meal_foods"

    meal_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("meals.id", ondelete="CASCADE"),
        primary_key=True,
    )
    food_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("foods.id", ondelete="CASCADE"),
        primary_key=True,
    )
    quantity_g: Mapped[float] = mapped_column(
        Numeric(7, 2),
        nullable=False,
        comment="Portion weight in grams",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    # Relationships back to parent models
    meal: Mapped["Meal"] = relationship("Meal", back_populates="meal_foods")  # noqa: F821
    food: Mapped["Food"] = relationship("Food", back_populates="meal_foods")  # noqa: F821


# ---------------------------------------------------------------------------
# Association model: Recipe <-> Food  (with quantity)
# ---------------------------------------------------------------------------

class RecipeFood(Base):
    """
    Represents a food ingredient inside a recipe, with its quantity.
    """

    __tablename__ = "recipe_foods"

    recipe_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("recipes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    food_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("foods.id", ondelete="CASCADE"),
        primary_key=True,
    )
    quantity_g: Mapped[float] = mapped_column(
        Numeric(7, 2),
        nullable=False,
        comment="Ingredient weight in grams",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    # Relationships back to parent models
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="recipe_foods")  # noqa: F821
    food: Mapped["Food"] = relationship("Food", back_populates="recipe_foods")  # noqa: F821
