from datetime import datetime
from typing import Optional, Dict
from typing_extensions import Annotated
from pydantic import BaseModel, Field, field_validator


PositiveInt = Annotated[int, Field(gt=0)]
DurationMinutes = Annotated[int, Field(gt=0, le=300)]
RestSeconds = Annotated[int, Field(ge=0, le=600)]
WeightKg = Annotated[float, Field(ge=0, le=1000)]


# ----------------------------
# Planned Session
# ----------------------------

class PlannedSessionBase(BaseModel):
    planned_date: datetime
    summary: str
    goal_progress_feedback: str
    intensity: Optional[str] = None
    estimated_duration_minutes: Optional[DurationMinutes] = None
    plan_payload: Optional[Dict] = None

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
    created: datetime
    updated: datetime

    model_config = {
        "from_attributes": True
    }


# ----------------------------
# Logged Session
# ----------------------------

class LoggedSessionCreate(BaseModel):
    planned_session_id: PositiveInt
    actual_date: Optional[datetime] = None


class LoggedSessionOut(BaseModel):
    id: int
    planned_session_id: int
    actual_date: Optional[datetime]
    completed: bool
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
    logged_session_id: int

    model_config = {
        "from_attributes": True
    }
