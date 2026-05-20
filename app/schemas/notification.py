from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from app.models.enums import NotificationType
from app.schemas.user import PublicUserOut


class NotificationOut(BaseModel):
    id: int
    type: NotificationType
    actor: Optional[PublicUserOut] = None
    meta: Optional[Any] = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
