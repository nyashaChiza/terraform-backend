from datetime import date, datetime
from typing import Optional, List
from typing_extensions import Annotated
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class GoalType(str, Enum):
    weight_loss = "WeightLoss"
    muscle_gain = "MuscleGain"
    endurance = "Endurance"
    strength = "Strength"
    custom = "Custom"


class GoalStatus(str, Enum):
    active = "Active"
    completed = "Completed"
    abandoned = "Abandoned"


PositiveFloat = Annotated[float, Field(gt=0)]
WeightKg = Annotated[float, Field(gt=0, le=300)]


# ----------------------------
# Goal Base
# ----------------------------

class GoalBase(BaseModel):
    title: Annotated[str, Field(min_length=3, max_length=100)]
    description: Optional[Annotated[str, Field(max_length=500)]] = None
    goal_type: GoalType
    target_value: PositiveFloat
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
    starting_value: Optional[PositiveFloat] = None


# ----------------------------
# Goal Progress Update
# ----------------------------

class GoalProgressUpdate(BaseModel):
    current_value: PositiveFloat


# ----------------------------
# Goal Close
# ----------------------------

class GoalClose(BaseModel):
    final_value: PositiveFloat
    before_images: List[str] = Field(
        min_length=1,
        description="At least one before image URL"
    )
    after_images: List[str] = Field(
        min_length=1,
        description="At least one after image URL"
    )
    notes: Optional[str] = Field(max_length=500)


# ----------------------------
# Goal Output
# ----------------------------

class GoalOut(GoalBase):
    id: int
    user_id: int
    status: GoalStatus
    current_value: Optional[float]
    created: datetime
    updated: datetime
    completed_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }
