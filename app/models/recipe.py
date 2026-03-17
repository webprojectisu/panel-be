from typing import List, Optional

from sqlalchemy import Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin
from app.models.associations import diet_plan_recipe


class Recipe(TimestampMixin, Base):
    """
    A reusable recipe that can be referenced by diet plans.
    Contains a list of food ingredients via RecipeFood.
    """

    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    preparation_time_minutes: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Total prep time in minutes"
    )
    calories: Mapped[Optional[float]] = mapped_column(
        Numeric(7, 2), nullable=True, comment="Estimated total kcal for the recipe"
    )

    # -----------------------------------------------------------------------
    # Relationships
    # -----------------------------------------------------------------------

    recipe_foods: Mapped[List["RecipeFood"]] = relationship(  # noqa: F821
        "RecipeFood",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    diet_plans: Mapped[List["DietPlan"]] = relationship(  # noqa: F821
        "DietPlan",
        secondary=diet_plan_recipe,
        back_populates="recipes",
    )

    def __repr__(self) -> str:
        return f"<Recipe id={self.id} title={self.title!r}>"
