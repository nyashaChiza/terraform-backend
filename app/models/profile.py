from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Enum, Date
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.enums import Gender, ExperienceLevel
from app.db.base import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    gender = Column(Enum(Gender))
    date_of_birth = Column(Date)
    weight = Column(Integer)  # in kgs
    height = Column(Integer)  # in centimeters
    phone_number = Column(String(255))
    experience_level = Column(Enum(ExperienceLevel))
    preferred_sessions_per_week = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="profile")

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "gender": self.gender.value if self.gender else None,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "weight": self.weight,
            "height": self.height,
            "phone_number": self.phone_number,
            "experience_level": self.experience_level.value if self.experience_level else None,
            "preferred_sessions_per_week": self.preferred_sessions_per_week,
            "user_id": self.user_id,
            "created": self.created.isoformat() if self.created else None,
            "updated": self.updated.isoformat() if self.updated else None
        }
