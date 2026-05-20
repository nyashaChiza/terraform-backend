from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, JSON
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    profile_picture_url = Column(String(500), nullable=True)
    is_discoverable = Column(Boolean, default=True, nullable=False)
    created = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_admin = Column(Boolean, default=False)
    profile = relationship("Profile", back_populates="user", uselist=False)
    goals = relationship("Goal", back_populates="user")
    sessions = relationship("Session", back_populates="user")
    progress_photos = relationship("ProgressPhoto", back_populates="user")

    @property
    def age(self) -> int:
        if self.profile and self.profile.date_of_birth:
            today = datetime.now(timezone.utc).date()
            dob = self.profile.date_of_birth
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return 0

