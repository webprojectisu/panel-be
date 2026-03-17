import enum
from datetime import time
from typing import List, Optional

from sqlalchemy import Enum, ForeignKey, Index, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class MealType(str, enum.Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"
    pre_workout = "pre_workout"
    post_workout = "post_workout"


class Meal(TimestampMixin, Base):
    """
    A single meal slot within a diet plan (e.g., Monday Breakfast).
    Can contain many foods via the MealFood association model.
    """

    __tablename__ = "meals"
    __table_args__ = (
        Index("ix_meals_diet_plan_id", "diet_plan_id"),
        Index("ix_meals_meal_type", "meal_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    diet_plan_id: Mapped[int] = mapped_column(
        ForeignKey("diet_plans.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    meal_type: Mapped[MealType] = mapped_column(Enum(MealType), nullable=False)
    scheduled_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # -----------------------------------------------------------------------
    # Relationships
    # -----------------------------------------------------------------------

    diet_plan: Mapped["DietPlan"] = relationship(  # noqa: F821
        "DietPlan",
        back_populates="meals",
    )
    meal_foods: Mapped[List["MealFood"]] = relationship(  # noqa: F821
        "MealFood",
        back_populates="meal",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Meal id={self.id} name={self.name!r} type={self.meal_type}>"
