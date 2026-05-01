from datetime import datetime
from typing import Dict, List, Optional
from typing_extensions import Annotated
from pydantic import BaseModel, Field, field_validator


SorenessScore = Annotated[int, Field(ge=0, le=5)]
Rating = Annotated[int, Field(ge=1, le=5)]


class ExerciseWeight(BaseModel):
    exercise_id: Optional[int] = None   # Optional: AI exercises always have it, but be lenient
    name: str = "Unknown"               # Default so missing name never causes 422
    weight_kg: float = Field(ge=0, le=500)


class SessionFeedbackCreate(BaseModel):
    soreness_per_muscle: Optional[Dict[str, SorenessScore]] = None
    joint_pain: bool
    effort_rating: Rating
    energy_level: Rating
    summary: Optional[str] = None       # UI labels this "optional" — match the intent
    weights_used: Optional[List[ExerciseWeight]] = None

    @field_validator("soreness_per_muscle")
    @classmethod
    def sanitize_muscle_keys(cls, v):
        """Strip whitespace from muscle names and drop any that are empty after stripping.
        This is defensive: the AI may occasionally produce padded or empty muscle groups.
        """
        if v is None:
            return v
        return {k.strip(): score for k, score in v.items() if k.strip()}


class SessionFeedbackOut(BaseModel):
    id: int
    session_id: int
    soreness_per_muscle: Optional[Dict[str, SorenessScore]] = None
    joint_pain: Optional[bool] = None
    effort_rating: Rating
    energy_level: Rating
    summary: Optional[str] = None
    weights_used: Optional[List[ExerciseWeight]] = None
    created: datetime
    updated: datetime

    model_config = {
        "from_attributes": True
    }
