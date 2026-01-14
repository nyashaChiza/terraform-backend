from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

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

@router.post(
    "/planned",
    response_model=PlannedSessionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_planned_session(
    session_in: PlannedSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SessionService.create_planned_session(
        db=db,
        user_id=current_user.id,
        planned_date=session_in.planned_date,
        estimated_duration_minutes=session_in.estimated_duration_minutes,
        plan_payload=session_in.plan_payload,
    )

@router.get(
    "/planned",
    response_model=list[PlannedSessionOut],
)
def list_planned_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SessionService.get_user_planned_sessions(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/completed",
    response_model=list[CompletedSessionOut],
)
def list_completed_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SessionService.get_user_completed_sessions(
        db=db,
        user_id=current_user.id,
    )

@router.post(
    "/log",
    response_model=LoggedSessionOut,
    status_code=status.HTTP_201_CREATED,
)
def log_session(
    session_in: LoggedSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return SessionService.log_session(
            db=db,
            planned_session_id=session_in.planned_session_id,
            user_id=current_user.id,
            actual_date=session_in.actual_date,
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planned session not found",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post(
    "/{logged_session_id}/complete",
    response_model=LoggedSessionOut,
)
def complete_logged_session(
    logged_session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return SessionService.complete_session(
            db=db,
            logged_session_id=logged_session_id,
            user_id=current_user.id,
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logged session not found",
        )


@router.post(
    "/{logged_session_id}/exercises",
    response_model=SessionExerciseOut,
    status_code=status.HTTP_201_CREATED,
)
def add_exercise(
    logged_session_id: int,
    exercise_in: SessionExerciseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return SessionService.add_exercise_to_session(
            db=db,
            logged_session_id=logged_session_id,
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
    "/{logged_session_id}/feedback",
    status_code=status.HTTP_201_CREATED,
)
def add_feedback(
    logged_session_id: int,
    feedback_in: SessionFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:

        return SessionService.add_feedback(
            db=db,
            logged_session_id=logged_session_id,
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
