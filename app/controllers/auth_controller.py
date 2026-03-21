"""
Authentication endpoints: login, register, logout, token refresh.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserBriefResponse,
)
from app.schemas.common import MessageResponse
from app.schemas.user import UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    user, token = auth_service.login(db, data.email, data.password)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserBriefResponse.model_validate(user),
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    data: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    user = auth_service.register(db, data)
    return UserResponse.model_validate(user)


@router.post("/logout", response_model=MessageResponse)
def logout(
    current_user: Annotated[User, Depends(get_current_user)],
) -> MessageResponse:
    # JWT is stateless; the client should discard its token.
    return MessageResponse(message="Successfully logged out.")


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    data: RefreshTokenRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    new_token = auth_service.refresh_token(db, data.refresh_token)
    # Decode to retrieve user_id for the brief response
    from app.core.security import decode_token

    payload = decode_token(new_token)
    user = db.get(User, int(payload["sub"]))
    return TokenResponse(
        access_token=new_token,
        token_type="bearer",
        user=UserBriefResponse.model_validate(user),
    )
