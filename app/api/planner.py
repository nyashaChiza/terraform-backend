from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict

from app.db.session import get_db
from app.models.user import User
from app.models.goal import Goal
from app.models.exercise import Exercise
from app.schemas.session import PlannedSessionOut
from app.core.dependencies import get_current_user
from app.services.planner_service import PlannerService

router = APIRouter(tags=["Planner"])


@router.post(
    "/generate",
    response_model=PlannedSessionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a new planned session for the user"
)
def generate_new_plan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger AI to generate the next workout session and save it
    in the PlannedSession table. Returns the newly created plan.
    """

    # Fetch all exercises available
    exercise_catalog: List[Dict] = [
        {
            "exercise_id": e.id,
            "name": e.name,
            "primary_muscle": e.primary_muscle.value,
            "stress_level": e.stress_level.value
        }
        for e in db.query(Exercise).all()
    ]

    latest_goal = (
        db.query(Goal)
        .filter(Goal.user_id == current_user.id)
        .order_by(Goal.created.desc())
        .first()
    )

    if not latest_goal:
        raise HTTPException(status_code=404, detail="User has no goals")

    current_goal = {
        "goal_type": latest_goal.type.value,
        # "description": latest_goal.description,
        # "start_date": latest_goal.start_date.isoformat() if latest_goal.start_date else None,
        "due_date": latest_goal.due_date.isoformat() if latest_goal.due_date else None,
        # "start_value": latest_goal.current_value,
        "target_value": latest_goal.target_value
    }


    try:
        planned_session = PlannerService.create_next_planned_session(
            db=db,
            user=current_user,
            goal=current_goal,
            exercise_catalog=exercise_catalog,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate plan: {str(e)}",
        )

    return planned_session
