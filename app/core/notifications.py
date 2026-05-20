from typing import Optional
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.enums import NotificationType


def create_notification(
    *,
    db: Session,
    user_id: int,
    type: NotificationType,
    actor_id: Optional[int] = None,
    meta: Optional[dict] = None,
) -> Notification:
    """
    Create and persist a notification.
    Called by friends.py, feed.py, etc.
    """
    notif = Notification(
        user_id=user_id,
        type=type,
        actor_id=actor_id,
        meta=meta,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif
