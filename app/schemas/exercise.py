# app/schemas/exercise.py
from pydantic import BaseModel, Field
from typing import List
from typing import Optional


class ExerciseBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    primary_muscle: str
    secondary_muscles: List[str] = []
    stress_level: str


class ExerciseCreate(ExerciseBase):
    pass



class ExerciseUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    primary_muscle: Optional[str] = None
    secondary_muscles: Optional[List[str]] = None
    stress_level: Optional[str] = None


class ExerciseOut(ExerciseBase):
    id: int

    class Config:
        from_attributes = True
