from datetime import date, datetime
from typing import Optional, List
from typing_extensions import Annotated
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


class GoalType(str, Enum):
    WeightLoss = "WeightLoss"
    MuscleGain = "MuscleGain"
    Endurance = "Endurance"
    Strength = "Strength"
    Custom = "Custom"


class GoalStatus(str, Enum):
    Active = "Active"
    Paused = "Paused"
    Completed = "Completed"
    Abandoned = "Abandoned"


PositiveFloat = Annotated[float, Field(gt=0)]
NonNegativeFloat = Annotated[float, Field(ge=0)]
WeightKg = Annotated[float, Field(gt=0, le=300)]


# ----------------------------
# Goal Base
# ----------------------------

class GoalBase(BaseModel):
    type: GoalType
    description: Optional[str] = None
    target_value: Optional[PositiveFloat]
    start_date: date
    due_date: date

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v, info):
        start = info.data.get("start_date")
        if start and v <= start:
            raise ValueError("due_date must be after start_date")
        return v



# ----------------------------
# Goal Create
# ----------------------------

class GoalCreate(GoalBase):
    starting_value: Optional[NonNegativeFloat] = None

# ----------------------------
# Goal Progress Update
# ----------------------------

class GoalProgressUpdate(BaseModel):
    current_value: NonNegativeFloat


# ----------------------------
# Goal Close
# ----------------------------

class GoalClose(BaseModel):
    final_value: PositiveFloat
    before_images: List[str] = Field(min_length=1)
    after_images: List[str] = Field(min_length=1)
    notes: Optional[str] = Field(max_length=500)



# ----------------------------
# Goal Output
# ----------------------------

class GoalOut(GoalBase):
    id: int
    user_id: int
    status: GoalStatus
    starting_value: float
    current_value: float
    start_date: datetime
    due_date: datetime
    created: datetime
    updated: datetime

    # Session-count progress — target_sessions intentionally omitted
    completed_sessions: Optional[int] = 0   # Optional handles NULL in legacy DB rows
    progress_pct: float = 0.0

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def compute_progress_pct(cls, data):
        """
        Derive progress_pct from the ORM object before Pydantic processes it.
        target_sessions is read here but never included in the output schema.
        """
        if hasattr(data, "__dict__"):
            # ORM instance
            completed = getattr(data, "completed_sessions", 0) or 0
            target    = getattr(data, "target_sessions", None)
            if target and target > 0:
                data.__dict__["progress_pct"] = round(min(completed / target * 100, 100), 1)
            else:
                data.__dict__["progress_pct"] = 0.0
        return data

# ----------------------------
# Goal Update


class GoalUpdate(BaseModel):
    type: GoalType
    description: Optional[Annotated[str, Field(max_length=500)]] = None
    target_value: Optional[PositiveFloat] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v, info):
        # Only validate if both dates are present (PATCH-safe)
        start = info.data.get("start_date")
        if start and v and v <= start:
            raise ValueError("due_date must be after start_date")
        return v
