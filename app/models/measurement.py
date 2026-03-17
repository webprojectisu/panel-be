from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Measurement(Base):
    """
    A snapshot of a client's body metrics at a specific point in time.
    No updated_at — measurements are immutable records, not editable.
    BMI is stored explicitly to preserve historical accuracy.
    """

    __tablename__ = "measurements"
    __table_args__ = (
        Index("ix_measurements_client_id", "client_id"),
        Index("ix_measurements_recorded_at", "recorded_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Body metrics — Numeric(5, 2) covers up to 999.99 which is sufficient
    height_cm: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    weight_kg: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    bmi: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    body_fat_percentage: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    waist_cm: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    hip_cm: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    chest_cm: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="When this measurement was taken",
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # -----------------------------------------------------------------------
    # Relationships
    # -----------------------------------------------------------------------

    client: Mapped["Client"] = relationship(  # noqa: F821
        "Client",
        back_populates="measurements",
    )

    def __repr__(self) -> str:
        return (
            f"<Measurement id={self.id} client_id={self.client_id} "
            f"weight_kg={self.weight_kg} recorded_at={self.recorded_at}>"
        )
