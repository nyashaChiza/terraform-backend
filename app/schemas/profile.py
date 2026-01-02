from datetime import date, datetime
from typing import Optional
from typing_extensions import Annotated
from pydantic import BaseModel, Field
from enum import Enum


class Gender(str, Enum):
    male = "Male"
    female = "Female"

class ExperienceLevel(str, Enum):
    Beginner = "Beginner"
    Intermediate = "Intermediate"
    Expert = "Expert"

PhoneNumber = Annotated[
    str,
    Field(
        min_length=7,
        max_length=20,
        pattern=r"^\+?[0-9]+$",
        description="E.164-compatible phone number"
    )
]

Height = Annotated[
    int,
    Field(
        ge=100,
        description="Height in centimeters"
    )
]


Weight = Annotated[
    int,
    Field(
        ge=30,
        description="Weight in kilograms"
    )
]

class ProfileBase(BaseModel):
    first_name: Annotated[str, Field(min_length=1, max_length=100)]
    last_name: Annotated[str, Field(min_length=1, max_length=100)]
    gender: Gender
    height: Height
    weight: Weight
    date_of_birth: date
    experience_level: ExperienceLevel
    preferred_sessions_per_week: Annotated[int, Field(ge=1, le=5)]
    phone_number: Optional[PhoneNumber] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    first_name: Optional[Annotated[str, Field(min_length=1, max_length=100)]] = None
    last_name: Optional[Annotated[str, Field(min_length=1, max_length=100)]] = None
    gender: Optional[Gender] = None
    phone_number: Optional[PhoneNumber] = None


class ProfileOut(ProfileBase):
    id: int
    user_id: int
    created: datetime
    updated: datetime

    model_config = {
        "from_attributes": True
    }
