"""
User (dietitian/admin) profile endpoints.
"""

from typing import Annotated, List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import ForbiddenException
from app.models.user import User, UserRole
from app.schemas.common import MessageResponse
from app.schemas.user import PasswordChangeRequest, UserResponse, UserUpdateRequest
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    user = user_service.get_me(db, current_user.id)
    return UserResponse.model_validate(user)


@router.put("/me", response_model=UserResponse)
def update_me(
    data: UserUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    user = user_service.update_me(db, current_user.id, data)
    return UserResponse.model_validate(user)


@router.put("/me/password", response_model=MessageResponse)
def change_password(
    data: PasswordChangeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    user_service.change_password(db, current_user.id, data)
    return MessageResponse(message="Password changed successfully.")


@router.get("", response_model=List[UserResponse])
def list_users(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> List[UserResponse]:
    if current_user.role != UserRole.admin:
        raise ForbiddenException("Only administrators can list all users.")
    users = user_service.list_users(db, skip=skip, limit=limit)
    return [UserResponse.model_validate(u) for u in users]
