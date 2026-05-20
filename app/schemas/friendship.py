from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.enums import FriendshipStatus
from app.schemas.user import PublicUserOut


class FriendshipOut(BaseModel):
    id: int
    status: FriendshipStatus
    created_at: datetime
    # whichever side is the "other" person
    other_user: PublicUserOut

    model_config = {"from_attributes": True}


class FriendRequestIn(BaseModel):
    addressee_id: int
