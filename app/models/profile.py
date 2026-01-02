from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Enum, Date
)
from sqlalchemy.orm import relationship
from datetime import datetime
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
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")
