"""
FastAPI dependency functions shared across controllers.
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedException
from app.core.security import decode_token
from app.db.base import get_db
from app.models.user import User

# Re-export get_db so other modules can import it from here
__all__ = ["get_db", "get_current_user"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    Decode the Bearer token and return the corresponding active User.

    Raises UnauthorizedException for:
    - Invalid / expired tokens
    - User not found in the database
    - Inactive users
    """
    payload = decode_token(token)

    user_id: int | None = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Token payload is missing 'sub' claim.")

    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise UnauthorizedException("Token 'sub' claim is not a valid user ID.")

    user: User | None = db.get(User, user_id_int)
    if user is None:
        raise UnauthorizedException("User not found.")

    if not user.is_active:
        raise UnauthorizedException("Account is deactivated.")

    return user
