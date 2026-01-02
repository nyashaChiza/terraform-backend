from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict

from app.db.session import get_db
from app.models.user import User
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
            "muscle_group": e.muscle_group,
            "default_sets": e.default_sets,
            "default_reps": e.default_reps,
            "rest_seconds": e.rest_seconds,
            "notes": e.notes,
        }
        for e in db.query(Exercise).all()
    ]

    # Example: fetch current goal from user profile or service
    current_goal: Dict = {
        "goal_type": current_user.goals.last().type,
        "target_value": current_user.goals.last().target_value,
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
