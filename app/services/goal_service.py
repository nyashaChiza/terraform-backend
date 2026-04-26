from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from typing import List
from app.core.config import Settings
from app.models.goal import Goal
from app.models.enums import GoalStatus

settings = Settings()

class GoalService:
    """
    Handles business logic for fitness/body goals.
    """

    @staticmethod
    def create_goal(
        db: Session,
        *,
        user_id: int,
        type,
        description: str | None,
        target_value: float | None,
        start_date,
        due_date,
        starting_value: float | None = None
    ) -> Goal:

        # Enforce single active goal
        active_goal = (
            db.query(Goal)
            .filter(
                Goal.user_id == user_id,
                Goal.status == GoalStatus.Active
            )
            .first()
        )
        if active_goal:
            raise ValueError("User already has an active goal")

        initial = starting_value or 0.0
        goal = Goal(
            user_id=user_id,
            type=type,
            description=description,
            target_value=target_value,
            starting_value=initial,
            current_value=initial,
            start_date=start_date,
            due_date=due_date,
            status=GoalStatus.Active
        )

        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def get_user_goals(db: Session, user_id: int) -> List[Goal]:
        return (
            db.query(Goal)
            .filter(Goal.user_id == user_id)
            .order_by(Goal.created.desc())
            .all()
        )

    @staticmethod
    def get_goal_by_id(
        db: Session,
        goal_id: int,
        user_id: int
    ) -> Goal:

        goal = (
            db.query(Goal)
            .filter(
                Goal.id == goal_id,
                Goal.user_id == user_id
            )
            .first()
        )

        if not goal:
            raise NoResultFound("Goal not found")

        return goal

    @staticmethod
    def update_goal(
        db: Session,
        goal_id: int,
        user_id: int,
        updates,  # GoalUpdate Pydantic model
    ) -> Goal:

        goal = GoalService.get_goal_by_id(
            db=db,
            goal_id=goal_id,
            user_id=user_id
        )

        if goal.status != GoalStatus.Active:
            raise ValueError("Only active goals can be updated")

        # Only apply fields that were explicitly sent; skip unknown model attributes
        allowed = {c.key for c in Goal.__table__.columns}
        for field, value in updates.model_dump(exclude_unset=True).items():
            if field in allowed:
                setattr(goal, field, value)

        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def update_progress(
        db: Session,
        *,
        goal_id: int,
        user_id: int,
        new_value: float
    ) -> Goal:

        goal = GoalService.get_goal_by_id(
            db=db,
            goal_id=goal_id,
            user_id=user_id
        )

        if goal.status != GoalStatus.Active:
            raise ValueError("Cannot update progress on inactive goal")

        if new_value < 0:
            raise ValueError("Progress value cannot be negative")

        goal.current_value = new_value
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def close_goal(
        db: Session,
        *,
        goal_id: int,
        user_id: int,
        final_value: float
    ) -> Goal:

        goal = GoalService.get_goal_by_id(
            db=db,
            goal_id=goal_id,
            user_id=user_id
        )

        if goal.status != GoalStatus.Active:
            raise ValueError("Goal already closed")

        goal.current_value = final_value
        goal.status = GoalStatus.Completed

        db.commit()
        db.refresh(goal)
        return goal


    @staticmethod
    def delete_goal(
        db: Session,
        *,
        goal_id: int,
        user_id: int
    ) -> None:
        goal = GoalService.get_goal_by_id(
            db=db,
            goal_id=goal_id,
            user_id=user_id
        )

        db.delete(goal)
        db.commit()
