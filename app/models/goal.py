from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, JSON
)
from sqlalchemy.orm import  relationship
from app.models.enums import GoalType, GoalStatus
from datetime import datetime
from app.db.base import Base

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(GoalType))
    target_value = Column(Float, nullable=True)
    starting_value = Column(Float, default=0.0)
    current_value = Column(Float, default=0.0)
    description = Column(String, nullable=True)
    start_date = Column(DateTime)
    due_date = Column(DateTime)
    status = Column(Enum(GoalStatus), default=GoalStatus.Active)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="goals")
    progress_photos = relationship("ProgressPhoto", back_populates="goal")
