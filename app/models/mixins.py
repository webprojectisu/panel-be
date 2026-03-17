from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import mapped_column, MappedColumn
from sqlalchemy.sql import func


class TimestampMixin:
    """
    Reusable mixin that adds created_at and updated_at columns to any model.

    - created_at: set once at INSERT, never changes.
    - updated_at: automatically refreshed on every UPDATE via onupdate.
    """

    created_at: MappedColumn[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
    updated_at: MappedColumn[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
