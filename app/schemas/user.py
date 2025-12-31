from datetime import datetime
from typing import Optional
from typing_extensions import Annotated
from pydantic import BaseModel, Field, EmailStr, field_validator


PasswordStr = Annotated[
    str,
    Field(
        min_length=8,
        max_length=128,
        description="Plain password, hashed before persistence"
    )
]


class UserBase(BaseModel):
    email: EmailStr


# ----------------------------
# User Create (Registration)
# ----------------------------

class UserCreate(UserBase):
    password: PasswordStr

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if v.lower() == v:
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        return v


# ----------------------------
# User Login
# ----------------------------

class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ----------------------------
# User Update (Very Limited)
# ----------------------------

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None


# ----------------------------
# User Output (Public / API Safe)
# ----------------------------

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created: datetime
    updated: datetime

    model_config = {
        "from_attributes": True
    }
