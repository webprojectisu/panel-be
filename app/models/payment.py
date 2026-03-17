import enum
from datetime import date
from typing import Optional

from sqlalchemy import Date, Enum, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"


class PaymentMethod(str, enum.Enum):
    cash = "cash"
    credit_card = "credit_card"
    debit_card = "debit_card"
    bank_transfer = "bank_transfer"
    online = "online"


class Payment(TimestampMixin, Base):
    """
    A payment record tied to both a client and the dietitian who received it.
    Amount uses Numeric (DECIMAL in MySQL) to avoid floating-point errors.
    """

    __tablename__ = "payments"
    __table_args__ = (
        Index("ix_payments_client_id", "client_id"),
        Index("ix_payments_dietitian_id", "dietitian_id"),
        Index("ix_payments_status", "status"),
        Index("ix_payments_payment_date", "payment_date"),
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

    # DECIMAL(10, 2) supports amounts up to 99,999,999.99
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="TRY", server_default="TRY",
        comment="ISO 4217 currency code, e.g. TRY, USD, EUR"
    )

    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod), nullable=False
    )
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus),
        nullable=False,
        default=PaymentStatus.pending,
        server_default=PaymentStatus.pending.value,
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # -----------------------------------------------------------------------
    # Relationships
    # -----------------------------------------------------------------------

    client: Mapped["Client"] = relationship(  # noqa: F821
        "Client",
        back_populates="payments",
    )
    dietitian: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="payments",
    )

    def __repr__(self) -> str:
        return (
            f"<Payment id={self.id} amount={self.amount} "
            f"status={self.status} client_id={self.client_id}>"
        )
