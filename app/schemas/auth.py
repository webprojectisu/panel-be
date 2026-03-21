"""
Authentication-related request/response schemas.
"""

import re
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.models.user import UserRole

# ---------------------------------------------------------------------------
# Shared validation helpers
# ---------------------------------------------------------------------------

_NAME_PATTERN = re.compile(
    r"^[A-Za-zğüşıöçĞÜŞİÖÇ][A-Za-zğüşıöçĞÜŞİÖÇ '\-]*$"
)


def _validate_full_name(value: str) -> str:
    value = value.strip()
    if len(value) < 2:
        raise ValueError("Name must be at least 2 characters long.")
    if len(value) > 150:
        raise ValueError("Name must not exceed 150 characters.")
    if value.replace(" ", "").replace("-", "").replace("'", "").isnumeric():
        raise ValueError("Name cannot be purely numeric.")
    if not _NAME_PATTERN.match(value):
        raise ValueError(
            "Name may only contain letters, spaces, hyphens, and apostrophes "
            "(including Turkish characters)."
        )
    return value


def _validate_password_complexity(value: str) -> str:
    if len(value) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if len(value) > 128:
        raise ValueError("Password must not exceed 128 characters.")
    if not any(c.isupper() for c in value):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not any(c.islower() for c in value):
        raise ValueError("Password must contain at least one lowercase letter.")
    if not any(c.isdigit() for c in value):
        raise ValueError("Password must contain at least one digit.")
    return value


def _validate_phone(value: str) -> str:
    value = value.strip()
    # Normalize: strip spaces, dashes, parens (keep leading +)
    has_plus = value.startswith("+")
    digits_only = re.sub(r"[\s\-\(\)]", "", value)
    if has_plus:
        digits_only = digits_only.lstrip("+")
    if not digits_only.isdigit():
        raise ValueError("Phone number must contain only digits (optionally prefixed with +).")
    if len(digits_only) < 7 or len(digits_only) > 15:
        raise ValueError("Phone number must be between 7 and 15 digits long.")
    return ("+" if has_plus else "") + digits_only


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    email: EmailStr
    password: str  # No complexity check on login — just required


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        return _validate_full_name(v)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password_complexity(v)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _validate_phone(v)


class UserBriefResponse(BaseModel):
    """Minimal user info embedded in token responses."""

    full_name: str
    email: str
    role: UserRole

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserBriefResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str
