from pydantic import BaseModel, ConfigDict, Field
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


class IncomingRequestOut(BaseModel):
    """One pending friend request the current user has received.

    `from_user` is aliased to `from` in JSON output to keep the legacy API
    contract intact while avoiding clashing with the Python `from` keyword
    on the server side.
    """
    friendship_id: int
    from_user: PublicUserOut = Field(serialization_alias="from")
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
