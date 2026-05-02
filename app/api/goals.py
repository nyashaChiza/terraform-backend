from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalOut, GoalUpdate, GoalProgressUpdate
from app.services.goal_service import GoalService
from app.services.profile_service import ProfileService
from app.core.dependencies import get_current_user

router = APIRouter(tags=["Goals"])

@router.post("/", response_model=GoalOut, status_code=status.HTTP_201_CREATED)
def create_goal(
    goal_in: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ensure user has profile
    profile_service = ProfileService(db)
    profile = profile_service.get_by_user(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must create a profile before creating a goal"
        )

    service = GoalService()
    try:
        goal = service.create_goal(
            db=db,
            user_id=current_user.id,
            type=goal_in.type,
            description=goal_in.description,
            target_value=goal_in.target_value,
            start_date=goal_in.start_date,
            due_date=goal_in.due_date,
            starting_value=goal_in.starting_value,
            profile=profile,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    return goal


@router.get("/current", response_model=List[GoalOut])
def get_current_goal(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = GoalService()
    goal = service.get_user_goals(db, current_user.id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active goal found"
        )
    return goal

@router.put("/{goal_id}", response_model=GoalOut)
def update_goal(
    goal_id: int,
    goal_in: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = GoalService()
    try:
        updated_goal = service.update_goal(db, goal_id, current_user.id, goal_in)
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return updated_goal


@router.patch("/{goal_id}/progress", response_model=GoalOut)
def update_goal_progress(
    goal_id: int,
    progress_in: GoalProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = GoalService()
    try:
        updated = service.update_progress(
            db=db,
            goal_id=goal_id,
            user_id=current_user.id,
            new_value=progress_in.current_value,
        )
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return updated

@router.post("/{goal_id}/close", response_model=GoalOut)
def close_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = GoalService()
    try:
        goal = service.get_goal_by_id(db, goal_id, current_user.id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    try:
        updated = service.close_goal(
            db=db,
            goal_id=goal_id,
            user_id=current_user.id,
            final_value=goal.current_value,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    return updated
