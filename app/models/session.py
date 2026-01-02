from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from app.models.enums import IntensityLevel


class PlannedSession(Base):
    __tablename__ = "planned_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    planned_date = Column(DateTime, nullable=False)
    estimated_duration_minutes = Column(Integer)
    plan_payload = Column(JSON)
    summary = Column(String)
    goal_progress_feedback = Column(String)
    intensity = Column(Enum(IntensityLevel))
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="planned_sessions")
    logged_sessions = relationship(
        "LoggedSession",
        back_populates="planned_session",
        cascade="all, delete-orphan",
    )


class LoggedSession(Base):
    __tablename__ = "logged_sessions"

    __table_args__ = (
        UniqueConstraint(
            "planned_session_id",
            name="uq_logged_sessions_planned_session_id",
        ),
    )

    id = Column(Integer, primary_key=True)
    planned_session_id = Column(
        Integer,
        ForeignKey("planned_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    actual_date = Column(DateTime)
    completed = Column(Boolean, default=False, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    planned_session = relationship(
        "PlannedSession",
        back_populates="logged_sessions",
    )
    exercises = relationship(
        "SessionExercise",
        back_populates="logged_session",
        cascade="all, delete-orphan",
    )
    feedback = relationship(
        "SessionFeedback",
        back_populates="logged_session",
        uselist=False,
        cascade="all, delete-orphan",
    )


class SessionExercise(Base):
    __tablename__ = "session_exercises"

    id = Column(Integer, primary_key=True)
    logged_session_id = Column(
        Integer,
        ForeignKey("logged_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    exercise_id = Column(
        Integer,
        ForeignKey("exercises.id"),
        nullable=False,
    )
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Float)
    rest_seconds = Column(Integer)

    logged_session = relationship(
        "LoggedSession",
        back_populates="exercises",
    )
    exercise = relationship(
        "Exercise",
        back_populates="session_exercises",
    )


class SessionFeedback(Base):
    __tablename__ = "session_feedbacks"

    __table_args__ = (
        UniqueConstraint(
            "logged_session_id",
            name="uq_session_feedback_logged_session",
        ),
    )

    id = Column(Integer, primary_key=True)
    logged_session_id = Column(
        Integer,
        ForeignKey("logged_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    soreness_per_muscle = Column(JSON)
    joint_pain = Column(Boolean, nullable=False)
    effort_rating = Column(Integer, nullable=False)
    energy_level = Column(Integer, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    logged_session = relationship(
        "LoggedSession",
        back_populates="feedback",
    )
