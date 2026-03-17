import enum
from datetime import date, time
from typing import Optional

from sqlalchemy import Date, Enum, ForeignKey, Index, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class AppointmentStatus(str, enum.Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"


class Appointment(TimestampMixin, Base):
    """
    A scheduled session between a dietitian and a client.
    Both dietitian_id and client_id are indexed for fast lookups.
    """

    __tablename__ = "appointments"
    __table_args__ = (
        Index("ix_appointments_dietitian_id", "dietitian_id"),
        Index("ix_appointments_client_id", "client_id"),
        Index("ix_appointments_appointment_date", "appointment_date"),
        Index("ix_appointments_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    dietitian_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )

    appointment_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)

    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus),
        nullable=False,
        default=AppointmentStatus.scheduled,
        server_default=AppointmentStatus.scheduled.value,
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # -----------------------------------------------------------------------
    # Relationships
    # -----------------------------------------------------------------------

    dietitian: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="appointments",
    )
    client: Mapped["Client"] = relationship(  # noqa: F821
        "Client",
        back_populates="appointments",
    )

    def __repr__(self) -> str:
        return (
            f"<Appointment id={self.id} date={self.appointment_date} "
            f"client_id={self.client_id} status={self.status}>"
        )
