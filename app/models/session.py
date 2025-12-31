from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, JSON
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class PlannedSession(Base):
    __tablename__ = "planned_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    planned_date = Column(DateTime)
    estimated_duration_minutes = Column(Integer)
    plan_payload = Column(JSON)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="planned_sessions")
    logged_sessions = relationship("LoggedSession", back_populates="planned_session")


class LoggedSession(Base):
    __tablename__ = "logged_sessions"

    id = Column(Integer, primary_key=True)
    planned_session_id = Column(Integer, ForeignKey("planned_sessions.id"), nullable=False)
    actual_date = Column(DateTime)
    completed = Column(Boolean, default=False)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    planned_session = relationship("PlannedSession", back_populates="logged_sessions")
    exercises = relationship("SessionExercise", back_populates="logged_session")
    feedback = relationship("SessionFeedback", back_populates="logged_session", uselist=False)


class SessionExercise(Base):
    __tablename__ = "session_exercises"

    id = Column(Integer, primary_key=True)
    logged_session_id = Column(Integer, ForeignKey("logged_sessions.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    sets = Column(Integer)
    reps = Column(Integer)
    weight = Column(Float)
    rest_seconds = Column(Integer)

    logged_session = relationship("LoggedSession", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="session_exercises")


class SessionFeedback(Base):
    __tablename__ = "session_feedbacks"

    id = Column(Integer, primary_key=True)
    logged_session_id = Column(Integer, ForeignKey("logged_sessions.id"), nullable=False)
    soreness_per_muscle = Column(JSON)  # e.g., {"Chest": 3, "Legs": 2}
    joint_pain = Column(Boolean)
    effort_rating = Column(Integer)
    energy_level = Column(Integer)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    logged_session = relationship("LoggedSession", back_populates="feedback")
