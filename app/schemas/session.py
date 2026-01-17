from datetime import datetime
from typing import Optional, Dict
from typing_extensions import Annotated
from pydantic import BaseModel, Field, field_validator
from app.schemas.feedback import SessionFeedbackOut
from app.models.enums import SessionStatus


PositiveInt = Annotated[int, Field(gt=0)]
DurationMinutes = Annotated[int, Field(gt=0, le=300)]
RestSeconds = Annotated[int, Field(ge=0, le=600)]
WeightKg = Annotated[float, Field(ge=0, le=1000)]


# ----------------------------
# Planned Session
# ----------------------------

class PlannedSessionBase(BaseModel):
    title: str
    summary: str
    goal_progress_feedback: str
    intensity: Optional[str] = None
    estimated_duration_minutes: Optional[DurationMinutes] = None
    plan_payload: Optional[Dict] = None
    created: datetime

    @field_validator("plan_payload")
    @classmethod
    def validate_plan_payload(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError("plan_payload must be a JSON object")
        return v


class PlannedSessionCreate(PlannedSessionBase):
    pass


class PlannedSessionOut(PlannedSessionBase):
    id: int
    user_id: int
    status: SessionStatus
    created: datetime
    updated: datetime

    model_config = {
        "from_attributes": True
    }


# ----------------------------
# Logged Session
# ----------------------------

class LoggedSessionCreate(BaseModel):
    session_id: PositiveInt
    

class LoggedSessionOut(BaseModel):
    id: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created: datetime
    updated: datetime

    model_config = {
        "from_attributes": True
    }


# ----------------------------
# Session Exercise
# ----------------------------

class SessionExerciseCreate(BaseModel):
    exercise_id: PositiveInt
    sets: Annotated[int, Field(gt=0, le=20)]
    reps: Annotated[int, Field(gt=0, le=100)]
    weight: Optional[WeightKg] = None
    rest_seconds: Optional[RestSeconds] = None


class SessionExerciseOut(SessionExerciseCreate):
    id: int
    session_id: int

    model_config = {
        "from_attributes": True
    }


class CompletedSessionOut(BaseModel):
    id: int
    session_id: int
    start_date: Optional[datetime]
    completed_date: Optional[datetime]
    created: datetime
    updated: datetime
    exercises: list[SessionExerciseOut] = []
    feedback: Optional[SessionFeedbackOut] = None

    model_config = {
        "from_attributes": True
    }

# ----------------------------
# Session Details
# ----------------------------

class SessionDetailsOut(BaseModel):
    id: int
    user_id: int
    title: str
    status: SessionStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_duration_minutes: Optional[DurationMinutes]
    actual_duration_minutes: Optional[int]
    intensity: Optional[str]
    plan_payload: Optional[Dict] = None
    summary: Optional[str]
    goal_progress_feedback: Optional[str]
    created: datetime
    updated: datetime
    exercises: list[SessionExerciseOut] = []
    feedback: Optional[SessionFeedbackOut] = None

    model_config = {
        "from_attributes": True
    }