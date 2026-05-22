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
    # Bumped on password change / logout-everywhere; embedded in JWTs.
    # All tokens with a stale `tv` claim are rejected, instantly invalidating
    # any outstanding access/refresh tokens.
    token_version = Column(Integer, nullable=False, default=0, server_default="0")
    created = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_admin = Column(Boolean, default=False)
    # All user-owned data cascades on user deletion. The DB also has
    # ON DELETE CASCADE on the FKs (via migrations) so this stays consistent
    # whether records are removed via the ORM or directly in SQL.
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    progress_photos = relationship("ProgressPhoto", back_populates="user", cascade="all, delete-orphan")

    @property
    def age(self) -> int:
        if self.profile and self.profile.date_of_birth:
            today = datetime.now(timezone.utc).date()
            dob = self.profile.date_of_birth
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return 0

