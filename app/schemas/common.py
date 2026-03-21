"""
Shared schema primitives reused across multiple domains.
"""

from pydantic import BaseModel, field_validator


class MessageResponse(BaseModel):
    """Generic success message response."""

    message: str


class PaginationParams(BaseModel):
    """Query-parameter schema for paginated list endpoints."""

    skip: int = 0
    limit: int = 20

    @field_validator("skip")
    @classmethod
    def skip_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("skip must be >= 0")
        return v

    @field_validator("limit")
    @classmethod
    def limit_range(cls, v: int) -> int:
        if v < 1 or v > 100:
            raise ValueError("limit must be between 1 and 100")
        return v
