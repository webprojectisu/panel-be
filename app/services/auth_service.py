"""
Authentication service: login, register, token refresh.
"""

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, decode_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import RegisterRequest


def login(db: Session, email: str, password: str) -> tuple[User, str]:
    """
    Authenticate a user by email and password.

    Returns (user, access_token) on success.
    Raises UnauthorizedException for invalid credentials or inactive account.
    """
    try:
        user: User | None = db.query(User).filter(User.email == email.strip().lower()).first()
        if user is None or not verify_password(password, user.password_hash):
            raise UnauthorizedException("Invalid email or password.")
        if not user.is_active:
            raise UnauthorizedException("Account is deactivated.")
        token = create_access_token(data={"sub": str(user.id)})
        return user, token
    except UnauthorizedException:
        raise
    except Exception as exc:
        raise UnauthorizedException("Authentication failed.") from exc


def register(db: Session, data: RegisterRequest) -> User:
    """
    Register a new user (dietitian).

    Raises ConflictException if the email is already taken.
    """
    try:
        existing = (
            db.query(User).filter(User.email == data.email.strip().lower()).first()
        )
        if existing is not None:
            raise ConflictException("A user with this email already exists.")
        
        new_user = User(
            full_name=data.full_name,
            email=data.email.strip().lower(),
            password_hash=hash_password(data.password),
            phone=data.phone,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except ConflictException:
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def refresh_token(db: Session, refresh_token_str: str) -> str:
    """
    Decode a refresh token and issue a new access token.

    Raises UnauthorizedException if token is invalid or user no longer exists.
    """
    try:
        payload = decode_token(refresh_token_str)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException("Invalid token payload.")

        user: User | None = db.get(User, int(user_id))
        if user is None or not user.is_active:
            raise UnauthorizedException("User not found or account is deactivated.")

        new_token = create_access_token(data={"sub": str(user.id)})
        return new_token
    except UnauthorizedException:
        raise
    except Exception as exc:
        raise UnauthorizedException("Token refresh failed.") from exc
