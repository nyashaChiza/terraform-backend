from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from app.db.session import get_db
from app.models.user import User
from app.models.goal import Goal
from app.models.session import Session as SessionModel
from app.models.exercise import Exercise
from app.models.equipment import UserEquipment
from app.models.enums import SessionStatus, EquipmentCategory
from app.schemas.session import PlannedSessionOut
from app.core.dependencies import get_current_user
from app.services.planner_service import PlannerService


router = APIRouter(tags=["Planner"])


@router.get(
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
    Trigger AI to generate the next workout session.
    Filters the exercise catalog to only include exercises
    matching the user's selected equipment. Bodyweight exercises
    are always included regardless of selection.
    """

    # Fetch the user's selected equipment categories
    user_equipment_rows = (
        db.query(UserEquipment)
        .filter(UserEquipment.user_id == current_user.id)
        .all()
    )

    # Resolve category for each selected equipment item
    from app.models.equipment import Equipment as EquipmentModel
    selected_equipment_ids = {row.equipment_id for row in user_equipment_rows}
    selected_items = (
        db.query(EquipmentModel)
        .filter(EquipmentModel.id.in_(selected_equipment_ids))
        .all()
        if selected_equipment_ids else []
    )
    selected_categories = {item.category for item in selected_items}

    # Always include bodyweight
    selected_categories.add(EquipmentCategory.bodyweight)

    # Build exercise catalog — filter by equipment category if user has selections,
    # otherwise fall back to the full catalog (no equipment set up yet)
    all_exercises = db.query(Exercise).all()
    if selected_equipment_ids:
        filtered = [
            e for e in all_exercises
            if e.equipment_category is None or e.equipment_category in selected_categories
        ]
        # Safety fallback: if filter leaves fewer than 10 exercises use full catalog
        exercise_pool = filtered if len(filtered) >= 10 else all_exercises
    else:
        exercise_pool = all_exercises

    exercise_catalog: List[Dict] = [
        {
            "exercise_id": e.id,
            "name": e.name,
            "primary_muscle": e.primary_muscle.value,
            "stress_level": e.stress_level.value,
            "equipment_category": e.equipment_category.value if e.equipment_category else "bodyweight",
        }
        for e in exercise_pool
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
        "description": latest_goal.description,
        "due_date": latest_goal.due_date.isoformat() if latest_goal.due_date else None,
    }

    latest_planned = (
        db.query(SessionModel)
        .filter(SessionModel.user_id == current_user.id)
        .order_by(SessionModel.created.desc())
        .first()
    )
    if latest_planned and latest_planned.status in (SessionStatus.PLANNED, SessionStatus.STARTED):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You must complete and log your current planned session before generating a new one."
        )

    try:
        planned_session = PlannerService.create_next_planned_session(
            db=db,
            user=current_user,
            goal=current_goal,
            exercise_catalog=exercise_catalog,
            available_equipment_categories=[c.value for c in selected_categories],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate plan: {str(e)}",
        )

    return planned_session
