from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, JSON
)
from sqlalchemy.orm import  relationship
from app.models.enums import MuscleGroup, StressLevel
from datetime import datetime
from db.base import Base

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    primary_muscle = Column(Enum(MuscleGroup))
    secondary_muscles = Column(JSON)  # list of muscles
    stress_level = Column(Enum(StressLevel))
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session_exercises = relationship("SessionExercise", back_populates="exercise")
