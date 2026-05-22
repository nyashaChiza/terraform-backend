from datetime import datetime
from typing import Optional
from typing_extensions import Annotated
from pydantic import BaseModel, Field, EmailStr, field_validator


PasswordStr = Annotated[
    str,
    Field(
        min_length=8,
        max_length=30,
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
# Password Change (self-service)
# ----------------------------

class PasswordChange(BaseModel):
    current_password: str
    new_password: PasswordStr

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, v: str) -> str:
        if v.lower() == v:
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        return v


# ----------------------------
# Admin Password Reset
# ----------------------------

class AdminPasswordReset(BaseModel):
    new_password: str = Field(min_length=6, max_length=50)


# ----------------------------
# Account Deletion (self-service)
# ----------------------------

class AccountDelete(BaseModel):
    """Password confirmation required for self-service deletion."""
    password: str = Field(min_length=1)


# ----------------------------
# User Output (Public / API Safe)
# ----------------------------

class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    profile_picture_url: Optional[str] = None
    is_discoverable: bool = True
    created: datetime
    updated: datetime

    model_config = {
        "from_attributes": True
    }


class UsernameUpdate(BaseModel):
    username: str = Field(min_length=2, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")


class DiscoverabilityUpdate(BaseModel):
    is_discoverable: bool


class PublicUserOut(BaseModel):
    """Minimal public profile for discovery / friend lists."""
    id: int
    username: str
    profile_picture_url: Optional[str] = None

    model_config = {"from_attributes": True}
