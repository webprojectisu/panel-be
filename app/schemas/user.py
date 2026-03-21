"""
User (dietitian / admin) request and response schemas.
"""

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.models.user import UserRole
from app.schemas.auth import _validate_full_name, _validate_password_complexity, _validate_phone


class UserResponse(BaseModel):
    """Full user representation returned to clients."""

    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    """Partial update for the authenticated user's own profile."""

    full_name: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _validate_full_name(v)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _validate_phone(v)


class PasswordChangeRequest(BaseModel):
    """Schema for changing the authenticated user's password."""

    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return _validate_password_complexity(v)
