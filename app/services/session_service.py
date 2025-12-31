from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from datetime import datetime
from typing import List, Dict, Any

from app.models.session import (
    PlannedSession,
    LoggedSession,
    SessionExercise,
    SessionFeedback,
)


class SessionService:
    """
    Handles workout session lifecycle:
    Planned → Logged → Completed → Feedback
    """

    # ------------------------
    # Planned Sessions
    # ------------------------

    @staticmethod
    def create_planned_session(
        db: Session,
        *,
        user_id: int,
        planned_date: datetime,
        estimated_duration_minutes: int | None,
        plan_payload: Dict[str, Any] | None,
    ) -> PlannedSession:
        planned = PlannedSession(
            user_id=user_id,
            planned_date=planned_date,
            estimated_duration_minutes=estimated_duration_minutes,
            plan_payload=plan_payload,
        )

        db.add(planned)
        db.commit()
        db.refresh(planned)
        return planned

    @staticmethod
    def get_user_planned_sessions(
        db: Session,
        *,
        user_id: int
    ) -> List[PlannedSession]:
        return (
            db.query(PlannedSession)
            .filter(PlannedSession.user_id == user_id)
            .order_by(PlannedSession.planned_date.desc())
            .all()
        )

    # ------------------------
    # Logged Sessions
    # ------------------------

    @staticmethod
    def log_session(
        db: Session,
        *,
        planned_session_id: int,
        user_id: int,
        actual_date: datetime | None = None
    ) -> LoggedSession:
        planned = (
            db.query(PlannedSession)
            .filter(
                PlannedSession.id == planned_session_id,
                PlannedSession.user_id == user_id,
            )
            .first()
        )

        if not planned:
            raise NoResultFound("Planned session not found")

        # Prevent duplicate logs
        existing = (
            db.query(LoggedSession)
            .filter(LoggedSession.planned_session_id == planned_session_id)
            .first()
        )

        if existing:
            raise ValueError("Session already logged")

        logged = LoggedSession(
            planned_session_id=planned_session_id,
            actual_date=actual_date or datetime.utcnow(),
            completed=False,
        )

        db.add(logged)
        db.commit()
        db.refresh(logged)
        return logged

    @staticmethod
    def complete_session(
        db: Session,
        *,
        logged_session_id: int,
        user_id: int
    ) -> LoggedSession:
        logged = (
            db.query(LoggedSession)
            .join(PlannedSession)
            .filter(
                LoggedSession.id == logged_session_id,
                PlannedSession.user_id == user_id,
            )
            .first()
        )

        if not logged:
            raise NoResultFound("Logged session not found")

        logged.completed = True
        db.commit()
        db.refresh(logged)
        return logged

    # ------------------------
    # Exercises
    # ------------------------

    @staticmethod
    def add_exercise_to_session(
        db: Session,
        *,
        logged_session_id: int,
        user_id: int,
        exercise_id: int,
        sets: int,
        reps: int,
        weight: float | None,
        rest_seconds: int | None,
    ) -> SessionExercise:
        logged = (
            db.query(LoggedSession)
            .join(PlannedSession)
            .filter(
                LoggedSession.id == logged_session_id,
                PlannedSession.user_id == user_id,
            )
            .first()
        )

        if not logged:
            raise NoResultFound("Logged session not found")

        exercise = SessionExercise(
            logged_session_id=logged_session_id,
            exercise_id=exercise_id,
            sets=sets,
            reps=reps,
            weight=weight,
            rest_seconds=rest_seconds,
        )

        db.add(exercise)
        db.commit()
        db.refresh(exercise)
        return exercise

    # ------------------------
    # Feedback
    # ------------------------

    @staticmethod
    def add_feedback(
        db: Session,
        *,
        logged_session_id: int,
        user_id: int,
        soreness_per_muscle: Dict[str, int] | None,
        joint_pain: bool,
        effort_rating: int,
        energy_level: int,
    ) -> SessionFeedback:
        logged = (
            db.query(LoggedSession)
            .join(PlannedSession)
            .filter(
                LoggedSession.id == logged_session_id,
                PlannedSession.user_id == user_id,
            )
            .first()
        )

        if not logged:
            raise NoResultFound("Logged session not found")

        if logged.feedback:
            raise ValueError("Feedback already exists for this session")

        feedback = SessionFeedback(
            logged_session_id=logged_session_id,
            soreness_per_muscle=soreness_per_muscle,
            joint_pain=joint_pain,
            effort_rating=effort_rating,
            energy_level=energy_level,
        )

        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback
