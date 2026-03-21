"""
User (dietitian/admin) management service.
"""

from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, NotFoundException
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import PasswordChangeRequest, UserUpdateRequest


def get_me(db: Session, user_id: int) -> User:
    """Return the user identified by *user_id*."""
    try:
        user: User | None = db.get(User, user_id)
        if user is None:
            raise NotFoundException("User not found.")
        return user
    except NotFoundException:
        raise
    except Exception as exc:
        raise exc


def update_me(db: Session, user_id: int, data: UserUpdateRequest) -> User:
    """Update the authenticated user's own profile."""
    try:
        user = get_me(db, user_id)
        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        db.commit()
        db.refresh(user)
        return user
    except (NotFoundException, BadRequestException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def change_password(db: Session, user_id: int, data: PasswordChangeRequest) -> None:
    """
    Change the authenticated user's password after verifying the current one.

    Raises BadRequestException if the current password is incorrect.
    """
    try:
        user = get_me(db, user_id)
        if not verify_password(data.current_password, user.password_hash):
            raise BadRequestException("Current password is incorrect.")
        user.password_hash = hash_password(data.new_password)
        db.commit()
    except (NotFoundException, BadRequestException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def list_users(db: Session, skip: int = 0, limit: int = 20) -> List[User]:
    """Return all users (admin-only operation)."""
    try:
        return db.query(User).offset(skip).limit(limit).all()
    except Exception as exc:
        raise exc
