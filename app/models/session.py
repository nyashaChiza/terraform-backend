from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from app.models.enums import IntensityLevel, SessionStatus


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(String(60), nullable=False)

    status = Column(
        Enum(SessionStatus, native_enum=False),
        nullable=False,
        default=SessionStatus.PLANNED,
        index=True,
    )

    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    estimated_duration_minutes = Column(Integer)
    actual_duration_minutes = Column(Integer)

    intensity = Column(
        Enum(IntensityLevel, native_enum=False),
        nullable=False,
    )

    plan_payload = Column(JSON)
    summary = Column(String)
    goal_progress_feedback = Column(String)

    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user = relationship("User", back_populates="sessions")

    exercises = relationship(
        "SessionExercise",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    feedback = relationship(
        "SessionFeedback",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )


class SessionExercise(Base):
    __tablename__ = "session_exercises"

    id = Column(Integer, primary_key=True)

    session_id = Column(
        Integer,
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    exercise_id = Column(
        Integer,
        ForeignKey("exercises.id"),
        nullable=False,
    )

    sets = Column(Integer)
    reps = Column(Integer)
    weight = Column(Float)
    rest_seconds = Column(Integer)

    set_payload = Column(JSON)  # optional future-proofing

    session = relationship(
        "Session",
        back_populates="exercises",
    )

    exercise = relationship(
        "Exercise",
        back_populates="session_exercises",
    )


from sqlalchemy import UniqueConstraint


class SessionFeedback(Base):
    __tablename__ = "session_feedbacks"

    __table_args__ = (
        UniqueConstraint(
            "session_id",
            name="uq_session_feedback_session_id",
        ),
    )

    id = Column(Integer, primary_key=True)
    session_id = Column(
        Integer,
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    soreness_per_muscle = Column(JSON)
    joint_pain = Column(JSON)
    effort_rating = Column(Integer, nullable=False)
    energy_level = Column(Integer, nullable=False)
    summary = Column(String)
    weights_used = Column(JSON)  # [{"exercise_id": 1, "name": "Bench Press", "weight_kg": 60.0}]

    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    session = relationship(
        "Session",
        back_populates="feedback",
    )
