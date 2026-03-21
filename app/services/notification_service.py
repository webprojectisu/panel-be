"""
Notification management service.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.notification import Notification


def list_notifications(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    is_read: Optional[bool] = None,
) -> List[Notification]:
    try:
        query = db.query(Notification).filter(Notification.user_id == user_id)
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
        return (
            query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
        )
    except Exception as exc:
        raise exc


def mark_as_read(db: Session, notification_id: int, user_id: int) -> Notification:
    try:
        notification: Notification | None = db.get(Notification, notification_id)
        if notification is None:
            raise NotFoundException(
                f"Notification with id={notification_id} not found."
            )
        if notification.user_id != user_id:
            raise ForbiddenException("You do not have access to this notification.")
        notification.is_read = True
        db.commit()
        db.refresh(notification)
        return notification
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        db.rollback()
        raise exc


def mark_all_as_read(db: Session, user_id: int) -> None:
    try:
        db.query(Notification).filter(
            Notification.user_id == user_id, Notification.is_read == False  # noqa: E712
        ).update({"is_read": True})
        db.commit()
    except Exception as exc:
        db.rollback()
        raise exc


def get_unread_count(db: Session, user_id: int) -> int:
    try:
        return (
            db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
            .count()
        )
    except Exception as exc:
        raise exc
