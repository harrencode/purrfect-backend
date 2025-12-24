

from src.auth.models import TokenData
# from . import models
from src.exceptions import NotificationNotFoundError, NotificationCreationError
import logging


from src.entities.notification import Notification
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timezone
from fastapi import HTTPException
from src.auth.models import TokenData
# from . import models
from src.exceptions import NotificationNotFoundError, NotificationCreationError
import logging

def create_notification_if_not_exists(
    db: Session,
    user_id: UUID,
    message: str,
    chat_id: UUID | None = None,
    report_id: UUID | None = None,
    notif_type: str | None = None,
):
    
    #Create a notification if one with the same (user_id, chat_id, report_id, notif_type)
    #does not already exist.
    

    try:
        # Check for existing similar notification to avoid duplicates
        existing = (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.chat_id == chat_id,
                Notification.report_id == report_id,
                Notification.notif_type == notif_type,
            )
            .first()
        )

        if existing:
            logging.info(
                f"[Notifications] Skipped duplicate {notif_type} notification for user {user_id}"
            )
            return existing

        # Create new notification
        notif = Notification(
            user_id=user_id,
            message=message,
            chat_id=chat_id,
            report_id=report_id,
            notif_type=notif_type,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        logging.info(
            f"[Notifications] Created new {notif_type or 'generic'} notification for user {user_id}"
        )
        return notif

    except Exception as e:
        logging.error(f"[Notifications] Failed to create notification: {e}")
        db.rollback()
        raise


def mark_notification_viewed(db: Session, notif_id: UUID, user_id: UUID):
    notif = (
        db.query(Notification)
        .filter(
            Notification.notif_id == notif_id,
            Notification.user_id == user_id,
        )
        .first()
    )
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.viewed = True
    db.commit()
    return notif


def get_notifications(current_user: TokenData, db: Session):
    return db.query(Notification).filter(Notification.user_id == current_user.get_uuid()).all()


def get_notification_by_id(current_user: TokenData, db: Session, notif_id: UUID):
    notif = db.query(Notification).filter(Notification.notif_id == notif_id, Notification.user_id == current_user.get_uuid()).first()
    if not notif:
        raise NotificationNotFoundError(notif_id)
    return notif