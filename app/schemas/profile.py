from datetime import datetime
from typing import Optional
from typing_extensions import Annotated
from pydantic import BaseModel, Field
from enum import Enum


class Gender(str, Enum):
    male = "Male"
    female = "Female"


PhoneNumber = Annotated[
    str,
    Field(
        min_length=7,
        max_length=20,
        pattern=r"^\+?[0-9]+$",
        description="E.164-compatible phone number"
    )
]


class ProfileBase(BaseModel):
    first_name: Annotated[str, Field(min_length=1, max_length=100)]
    last_name: Annotated[str, Field(min_length=1, max_length=100)]
    gender: Gender
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
