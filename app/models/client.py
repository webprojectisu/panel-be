import enum
from datetime import date
from typing import List, Optional

from sqlalchemy import Date, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Gender(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class Client(TimestampMixin, Base):
    """
    Represents a client who is assigned to a dietitian.
    One dietitian can manage many clients.
    """

    __tablename__ = "clients"
    __table_args__ = (
        Index("ix_clients_dietitian_id", "dietitian_id"),
        Index("ix_clients_email", "email"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    dietitian_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[Gender]] = mapped_column(Enum(Gender), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # -----------------------------------------------------------------------
    # Relationships
    # -----------------------------------------------------------------------

    dietitian: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="clients",
    )
    appointments: Mapped[List["Appointment"]] = relationship(  # noqa: F821
        "Appointment",
        back_populates="client",
        cascade="all, delete-orphan",
    )
    measurements: Mapped[List["Measurement"]] = relationship(  # noqa: F821
        "Measurement",
        back_populates="client",
        cascade="all, delete-orphan",
    )
    diet_plans: Mapped[List["DietPlan"]] = relationship(  # noqa: F821
        "DietPlan",
        back_populates="client",
        cascade="all, delete-orphan",
    )
    payments: Mapped[List["Payment"]] = relationship(  # noqa: F821
        "Payment",
        back_populates="client",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Client id={self.id} name={self.full_name!r} dietitian_id={self.dietitian_id}>"
