from datetime import datetime
from typing import Dict, Optional
from typing_extensions import Annotated
from pydantic import BaseModel, Field, field_validator


SorenessScore = Annotated[int, Field(ge=0, le=5)]
Rating = Annotated[int, Field(ge=1, le=5)]


class SessionFeedbackCreate(BaseModel):
    soreness_per_muscle: Optional[Dict[str, SorenessScore]] = None
    joint_pain: bool
    effort_rating: Rating
    energy_level: Rating
    summary: str

    @field_validator("soreness_per_muscle")
    @classmethod
    def validate_muscle_keys(cls, v):
        if v is None:
            return v

        for muscle in v.keys():
            if not muscle.strip():
                raise ValueError("Muscle names cannot be empty")

        return v


class SessionFeedbackOut(SessionFeedbackCreate):
    id: int
    logged_session_id: int
    created: datetime
    updated: datetime

    model_config = {
        "from_attributes": True
    }
