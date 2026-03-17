import enum
from datetime import date
from typing import List, Optional

from sqlalchemy import Date, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin
from app.models.associations import diet_plan_recipe


class DietPlanStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    completed = "completed"


class DietPlan(TimestampMixin, Base):
    """
    A structured nutrition plan created by a dietitian for a specific client.
    Can contain many meals and reference many recipes.
    """

    __tablename__ = "diet_plans"
    __table_args__ = (
        Index("ix_diet_plans_client_id", "client_id"),
        Index("ix_diet_plans_dietitian_id", "dietitian_id"),
        Index("ix_diet_plans_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )
    dietitian_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    status: Mapped[DietPlanStatus] = mapped_column(
        Enum(DietPlanStatus),
        nullable=False,
        default=DietPlanStatus.draft,
        server_default=DietPlanStatus.draft.value,
    )

    # -----------------------------------------------------------------------
    # Relationships
    # -----------------------------------------------------------------------

    client: Mapped["Client"] = relationship(  # noqa: F821
        "Client",
        back_populates="diet_plans",
    )
    dietitian: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="diet_plans",
    )
    meals: Mapped[List["Meal"]] = relationship(  # noqa: F821
        "Meal",
        back_populates="diet_plan",
        cascade="all, delete-orphan",
    )
    recipes: Mapped[List["Recipe"]] = relationship(  # noqa: F821
        "Recipe",
        secondary=diet_plan_recipe,
        back_populates="diet_plans",
    )

    def __repr__(self) -> str:
        return f"<DietPlan id={self.id} title={self.title!r} status={self.status}>"
