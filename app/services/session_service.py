from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound, IntegrityError
from datetime import datetime
from typing import List, Dict, Any, Optional

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

    # ========================
    # Internal helpers
    # ========================

    @staticmethod
    def _get_planned_session_for_user(
        db: Session,
        *,
        planned_session_id: int,
        user_id: int,
    ) -> PlannedSession:
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

        return planned

    @staticmethod
    def _get_logged_session_for_user(
        db: Session,
        *,
        logged_session_id: int,
        user_id: int,
    ) -> LoggedSession:
        logged = (
            db.query(LoggedSession)
            .join(
                PlannedSession,
                LoggedSession.planned_session_id == PlannedSession.id
            )
            .filter(
                LoggedSession.id == logged_session_id,
                PlannedSession.user_id == user_id,
            )
            .first()
        )


        if not logged:
            raise NoResultFound("Logged session not found")

        return logged

    # ========================
    # Planned Sessions
    # ========================

    @staticmethod
    def create_planned_session(
        db: Session,
        *,
        user_id: int,
        planned_date: datetime,
        estimated_duration_minutes: Optional[int],
        plan_payload: Optional[Dict[str, Any]],
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
        user_id: int,
    ) -> List[PlannedSession]:
        return (
            db.query(PlannedSession)
            .filter(PlannedSession.user_id == user_id)
            .order_by(PlannedSession.planned_date.desc())
            .all()
        )

    # ========================
    # Logged Sessions
    # ========================

    @staticmethod
    def log_session(
        db: Session,
        *,
        planned_session_id: int,
        user_id: int,
        actual_date: Optional[datetime] = None,
    ) -> LoggedSession:
        planned = SessionService._get_planned_session_for_user(
            db,
            planned_session_id=planned_session_id,
            user_id=user_id,
        )

        logged = LoggedSession(
            planned_session_id=planned.id,
            actual_date=actual_date or datetime.utcnow(),
            completed=False,
        )

        db.add(logged)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            # UNIQUE constraint violation on planned_session_id
            raise ValueError("Session already logged for this planned session")

        db.refresh(logged)
        return logged

    @staticmethod
    def complete_session(
        db: Session,
        *,
        logged_session_id: int,
        user_id: int,
    ) -> LoggedSession:
        logged = SessionService._get_logged_session_for_user(
            db,
            logged_session_id=logged_session_id,
            user_id=user_id,
        )

        if logged.completed:
            return logged  # idempotent

        logged.completed = True
        db.commit()
        db.refresh(logged)
        return logged

    # ========================
    # Exercises
    # ========================

    @staticmethod
    def add_exercise_to_session(
        db: Session,
        *,
        logged_session_id: int,
        user_id: int,
        exercise_id: int,
        sets: int,
        reps: int,
        weight: Optional[float],
        rest_seconds: Optional[int],
    ) -> SessionExercise:
        logged = SessionService._get_logged_session_for_user(
            db,
            logged_session_id=logged_session_id,
            user_id=user_id,
        )

        if logged.completed:
            raise ValueError("Cannot add exercises to a completed session")

        exercise = SessionExercise(
            logged_session_id=logged.id,
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

    # ========================
    # Feedback
    # ========================

    @staticmethod
    def add_feedback(
        db: Session,
        *,
        logged_session_id: int,
        user_id: int,
        soreness_per_muscle: Optional[Dict[str, int]],
        joint_pain: bool,
        effort_rating: int,
        energy_level: int,
    ) -> SessionFeedback:
        logged = SessionService._get_logged_session_for_user(
            db,
            logged_session_id=logged_session_id,
            user_id=user_id,
        )

        if not logged.completed:
            raise ValueError("Cannot add feedback to an incomplete session")

        if logged.feedback:
            raise ValueError("Feedback already exists for this session")

        feedback = SessionFeedback(
            logged_session_id=logged.id,
            soreness_per_muscle=soreness_per_muscle,
            joint_pain=joint_pain,
            effort_rating=effort_rating,
            energy_level=energy_level,
        )

        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback
