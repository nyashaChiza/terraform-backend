from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base
from app.models.enums import FriendshipStatus


class Friendship(Base):
    """
    Directed friendship record.
    requester_id → addressee_id with a status.
    A unique constraint on (requester_id, addressee_id) prevents duplicates.
    """
    __tablename__ = "friendships"
    __table_args__ = (
        UniqueConstraint("requester_id", "addressee_id", name="uq_friendship_pair"),
    )

    id = Column(Integer, primary_key=True)
    requester_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    addressee_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(FriendshipStatus), nullable=False, default=FriendshipStatus.pending)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    requester = relationship("User", foreign_keys=[requester_id])
    addressee = relationship("User", foreign_keys=[addressee_id])


class SessionReaction(Base):
    """
    A reaction (emoji) left by one user on another user's completed session.
    """
    __tablename__ = "session_reactions"
    __table_args__ = (
        UniqueConstraint("session_id", "reactor_id", name="uq_reaction_per_session_user"),
    )

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    reactor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    emoji = Column(String(10), nullable=False, default="💪")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    reactor = relationship("User", foreign_keys=[reactor_id])
    session = relationship("Session", foreign_keys=[session_id])
