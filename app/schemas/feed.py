from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.user import PublicUserOut


class ReactionOut(BaseModel):
    id: int
    reactor: PublicUserOut
    emoji: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedSessionOut(BaseModel):
    """A friend's completed session as it appears in the activity feed."""
    session_id: int
    user: PublicUserOut
    title: str
    summary: Optional[str] = None
    intensity: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None
    completed_at: datetime
    reactions: List[ReactionOut] = []
    # caller's own reaction emoji, or None
    my_reaction: Optional[str] = None

    model_config = {"from_attributes": True}


class ReactPayload(BaseModel):
    emoji: str = "💪"
