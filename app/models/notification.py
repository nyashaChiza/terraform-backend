from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base
from app.models.enums import NotificationType


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    # actor = the user who triggered the notification
    actor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    # optional extra payload (e.g. session_id for reaction notifications)
    meta = Column(JSON, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", foreign_keys=[user_id])
    actor = relationship("User", foreign_keys=[actor_id])
