import enum
from typing import List, Optional

from sqlalchemy import Boolean, Enum, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class UserRole(str, enum.Enum):
    admin = "admin"
    dietitian = "dietitian"


class User(TimestampMixin, Base):
    """
    Represents a dietitian (or admin) who uses the panel.
    This is the primary actor in the system.
    """

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        Index("ix_users_email", "email"),
        Index("ix_users_role", "role"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.dietitian,
        server_default=UserRole.dietitian.value,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="1",
    )

    # -----------------------------------------------------------------------
    # Relationships
    # -----------------------------------------------------------------------

    clients: Mapped[List["Client"]] = relationship(  # noqa: F821
        "Client",
        back_populates="dietitian",
        cascade="all, delete-orphan",
    )
    appointments: Mapped[List["Appointment"]] = relationship(  # noqa: F821
        "Appointment",
        back_populates="dietitian",
        cascade="all, delete-orphan",
    )
    diet_plans: Mapped[List["DietPlan"]] = relationship(  # noqa: F821
        "DietPlan",
        back_populates="dietitian",
        cascade="all, delete-orphan",
    )
    payments: Mapped[List["Payment"]] = relationship(  # noqa: F821
        "Payment",
        back_populates="dietitian",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[List["Notification"]] = relationship(  # noqa: F821
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role}>"
