"""
Notification endpoints.

IMPORTANT: /unread-count and /read-all must be registered BEFORE
/{notification_id} to avoid path conflicts.
"""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.notification import NotificationResponse, UnreadCountResponse
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationResponse])
def list_notifications(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    is_read: Optional[bool] = Query(default=None),
) -> List[NotificationResponse]:
    notifications = notification_service.list_notifications(
        db, current_user.id, skip=skip, limit=limit, is_read=is_read
    )
    return [NotificationResponse.model_validate(n) for n in notifications]


# IMPORTANT: /unread-count before /{notification_id}
@router.get("/unread-count", response_model=UnreadCountResponse)
def get_unread_count(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UnreadCountResponse:
    count = notification_service.get_unread_count(db, current_user.id)
    return UnreadCountResponse(count=count)


# IMPORTANT: /read-all before /{notification_id}
@router.put("/read-all", response_model=MessageResponse)
def mark_all_as_read(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    notification_service.mark_all_as_read(db, current_user.id)
    return MessageResponse(message="All notifications marked as read.")


@router.put("/{notification_id}/read", response_model=MessageResponse)
def mark_as_read(
    notification_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    notification_service.mark_as_read(db, notification_id, current_user.id)
    return MessageResponse(message="Notification marked as read.")
