from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.models.enums import SessionStatus
from app.models.session import (
    Session as SessionModel,
    SessionExercise,
    SessionFeedback,
)


class SessionService:
    """
    Handles workout session lifecycle:
    PLANNED → STARTED → COMPLETED → FEEDBACK
    """

    # ========================
    # Internal helpers
    # ========================

    @staticmethod
    def _get_session_for_user(
        db: Session,
        *,
        session_id: int,
        user_id: int,
    ) -> SessionModel:
        session = (
            db.query(SessionModel)
            .filter(
                SessionModel.id == session_id,
                SessionModel.user_id == user_id,
            )
            .first()
        )

        if not session:
            raise NoResultFound("Session not found")

        return session

    # ========================
    # Session creation & queries
    # ========================

    @staticmethod
    def create_session(
        db: Session,
        *,
        user_id: int,
        title: Optional[str],
        estimated_duration_minutes: Optional[int],
        plan_payload: Optional[Dict[str, Any]],
    ) -> SessionModel:
        session = SessionModel(
            user_id=user_id,
            title=title,
            estimated_duration_minutes=estimated_duration_minutes,
            plan_payload=plan_payload,
            status=SessionStatus.PLANNED,
        )

        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_user_sessions(
        db: Session,
        *,
        user_id: int,
        status: Optional[SessionStatus] = None,
    ) -> List[SessionModel]:
        q = db.query(SessionModel).filter(SessionModel.user_id == user_id)

        if status:
            q = q.filter(SessionModel.status == status)

        return q.order_by(SessionModel.created.desc()).all()

    # ========================
    # Lifecycle transitions
    # ========================

    @staticmethod
    def start_session(
        db: Session,
        *,
        session_id: int,
        user_id: int,
    ) -> SessionModel:
        session = SessionService._get_session_for_user(
            db,
            session_id=session_id,
            user_id=user_id,
        )

        if session.status != SessionStatus.PLANNED:
            raise ValueError("Only planned sessions can be started")

        session.status = SessionStatus.STARTED
        session.started_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def complete_session(
        db: Session,
        *,
        session_id: int,
        user_id: int,
    ) -> SessionModel:
        session = SessionService._get_session_for_user(
            db,
            session_id=session_id,
            user_id=user_id,
        )

        if session.status == SessionStatus.COMPLETED:
            return session  # idempotent

        if session.status != SessionStatus.STARTED:
            raise ValueError("Session must be started before completing")

        session.status = SessionStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
        return session

    # ========================
    # Exercises
    # ========================

    @staticmethod
    def add_exercise(
        db: Session,
        *,
        session_id: int,
        user_id: int,
        exercise_id: int,
        sets: int,
        reps: int,
        weight: Optional[float],
        rest_seconds: Optional[int],
    ) -> SessionExercise:
        session = SessionService._get_session_for_user(
            db,
            session_id=session_id,
            user_id=user_id,
        )

        if session.status == SessionStatus.COMPLETED:
            raise ValueError("Cannot modify a completed session")

        exercise = SessionExercise(
            session_id=session.id,
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
        session_id: int,
        user_id: int,
        soreness_per_muscle: Optional[Dict[str, int]],
        joint_pain: bool,
        effort_rating: int,
        energy_level: int,
        summary: Optional[str] = None,
    ) -> SessionFeedback:
        session = SessionService._get_session_for_user(
            db,
            session_id=session_id,
            user_id=user_id,
        )

        if session.status != SessionStatus.COMPLETED:
            raise ValueError("Feedback can only be added to completed sessions")

        if session.feedback:
            raise ValueError("Feedback already exists for this session")

        feedback = SessionFeedback(
            session_id=session.id,
            soreness_per_muscle=soreness_per_muscle,
            joint_pain=joint_pain,
            effort_rating=effort_rating,
            energy_level=energy_level,
            summary=summary,
        )

        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback
