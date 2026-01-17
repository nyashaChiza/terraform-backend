from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.enums import SessionStatus

from app.schemas.session import (
    PlannedSessionCreate,
    PlannedSessionOut,
    LoggedSessionCreate,
    LoggedSessionOut,
    SessionExerciseCreate,
    SessionExerciseOut,
    CompletedSessionOut,
)
from app.schemas.feedback import SessionFeedbackCreate

from app.services.session_service import SessionService

router = APIRouter(tags=["Sessions"])

@router.get(
    "",
    response_model=list[PlannedSessionOut],
)
def list_sessions_by_status(
    status_filter: SessionStatus = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SessionService.get_user_sessions(
        db=db,
        user_id=current_user.id,
        status=status_filter,
    )

@router.get(
    "/planned/latest",
    response_model=PlannedSessionOut,
)
def get_latest_planned_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = SessionService.get_user_sessions(
        db=db,
        user_id=current_user.id,
        status=SessionStatus.PLANNED,
    )
    if not sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No planned sessions found",
        )
    return sessions[0]  # Already sorted by created desc in service


@router.get(
    "/completed",
    response_model=list[CompletedSessionOut],
)
def list_completed_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SessionService.get_user_sessions(
        db=db,
        user_id=current_user.id,
        status=SessionStatus.COMPLETED,
    )

@router.post(
    "/{session_id}/start",
    response_model=LoggedSessionOut,
)
def start_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return SessionService.start_session(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post(
    "/{session_id}/complete",
    response_model=LoggedSessionOut,
)
def complete_logged_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return SessionService.complete_session(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logged/Started session not found",
        )


@router.post(
    "/{session_id}/exercises",
    response_model=SessionExerciseOut,
    status_code=status.HTTP_201_CREATED,
)
def add_exercise(
    session_id: int,
    exercise_in: SessionExerciseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return SessionService.add_exercise_to_session(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
            exercise_id=exercise_in.exercise_id,
            sets=exercise_in.sets,
            reps=exercise_in.reps,
            weight=exercise_in.weight,
            rest_seconds=exercise_in.rest_seconds,
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logged session not found",
        )

@router.post(
    "/{session_id}/feedback",
    status_code=status.HTTP_201_CREATED,
)
def add_feedback(
    session_id: int,
    feedback_in: SessionFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:

        return SessionService.add_feedback(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
            soreness_per_muscle=feedback_in.soreness_per_muscle,
            joint_pain=feedback_in.joint_pain,
            summary=feedback_in.summary,
            effort_rating=feedback_in.effort_rating,
            energy_level=feedback_in.energy_level,
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logged session not found",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
