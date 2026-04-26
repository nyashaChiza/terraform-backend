"""
Auto-calculates goal progress based on goal type and available data.

Called after:
  - Session feedback is submitted  (Strength / MuscleGain / Endurance)
  - Profile weight is updated       (WeightLoss)
"""

from sqlalchemy.orm import Session as DBSession

from app.models.goal import Goal
from app.models.session import Session as SessionModel, SessionFeedback
from app.models.profile import Profile
from app.models.enums import GoalStatus, GoalType, SessionStatus


def auto_update_goal_progress(
    db: DBSession,
    *,
    user_id: int,
    weights_used: list | None = None,
) -> Goal | None:
    """
    Finds the user's active goal and updates current_value automatically.

    weights_used: the list from the just-submitted feedback
                  (needed for Strength / MuscleGain calculation)

    Returns the updated Goal, or None if no active goal exists.
    """

    goal: Goal | None = (
        db.query(Goal)
        .filter(
            Goal.user_id == user_id,
            Goal.status == GoalStatus.Active,
        )
        .first()
    )

    if not goal or goal.target_value is None:
        return None

    new_value: float | None = None

    # ------------------------------------------------------------------
    # WeightLoss → current body weight from profile
    # ------------------------------------------------------------------
    if goal.type == GoalType.WeightLoss:
        profile: Profile | None = (
            db.query(Profile).filter(Profile.user_id == user_id).first()
        )
        if profile and profile.weight:
            new_value = float(profile.weight)

    # ------------------------------------------------------------------
    # Strength / MuscleGain → average weight used in this session
    # ------------------------------------------------------------------
    elif goal.type in (GoalType.Strength, GoalType.MuscleGain):
        if weights_used:
            valid = [
                w.get("weight_kg", 0)
                for w in weights_used
                if isinstance(w, dict) and w.get("weight_kg", 0) > 0
            ]
            if valid:
                new_value = round(sum(valid) / len(valid), 1)

    # ------------------------------------------------------------------
    # Endurance → completed sessions since goal start date
    # ------------------------------------------------------------------
    elif goal.type == GoalType.Endurance:
        count = (
            db.query(SessionModel)
            .filter(
                SessionModel.user_id == user_id,
                SessionModel.status == SessionStatus.COMPLETED,
                SessionModel.completed_at >= goal.start_date,
            )
            .count()
        )
        new_value = float(count)

    # Custom → no auto-calculation; user updates manually

    # ------------------------------------------------------------------
    # Persist if value changed
    # ------------------------------------------------------------------
    if new_value is not None and new_value != goal.current_value:
        goal.current_value = new_value
        db.commit()
        db.refresh(goal)

    return goal
