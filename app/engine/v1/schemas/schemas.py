from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class PlannedExercise(BaseModel):
    exercise_id: int
    name: str
    muscle_group: str
    sets: int = Field(gt=0, le=10)
    reps: int = Field(gt=0, le=50)
    rest_seconds: int = Field(ge=0, le=300)
    notes: Optional[str] = None


class PlannedSessionAI(BaseModel):
    title: str = Field(max_length=100)
    summary: str | None = ""
    goal_progress_feedback: str | None = ""
    estimated_duration_minutes: int = Field(gt=10, le=120)
    intensity: str  # deload | normal | push
    exercises: List[PlannedExercise]
