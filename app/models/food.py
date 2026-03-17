from typing import List, Optional

from sqlalchemy import Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Food(TimestampMixin, Base):
    """
    A reusable food item with nutritional information.
    Can be added to many meals and many recipes.
    All nutritional values are per 100g unless portion_size is specified.
    """

    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)

    # Nutritional values per 100g — Numeric(7, 2) allows up to 99999.99
    calories: Mapped[Optional[float]] = mapped_column(
        Numeric(7, 2), nullable=True, comment="kcal per 100g"
    )
    protein: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2), nullable=True, comment="grams per 100g"
    )
    carbs: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2), nullable=True, comment="grams per 100g"
    )
    fat: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2), nullable=True, comment="grams per 100g"
    )

    portion_size: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="e.g. '1 slice', '1 cup', '100g'"
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # -----------------------------------------------------------------------
    # Relationships (via association models)
    # -----------------------------------------------------------------------

    meal_foods: Mapped[List["MealFood"]] = relationship(  # noqa: F821
        "MealFood",
        back_populates="food",
        cascade="all, delete-orphan",
    )
    recipe_foods: Mapped[List["RecipeFood"]] = relationship(  # noqa: F821
        "RecipeFood",
        back_populates="food",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Food id={self.id} name={self.name!r} calories={self.calories}>"
