from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from typing import List

from app.models.goal import Goal


class GoalService:
    """
    Handles business logic for fitness/body goals.
    """

    @staticmethod
    def create_goal(
        db: Session,
        *,
        user_id: int,
        title: str,
        description: str | None,
        target_value: float
    ) -> Goal:
        goal = Goal(
            user_id=user_id,
            title=title,
            description=description,
            target_value=target_value,
        )

        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def get_user_goals(db: Session, *, user_id: int) -> List[Goal]:
        return (
            db.query(Goal)
            .filter(Goal.user_id == user_id)
            .order_by(Goal.created.desc())
            .all()
        )

    @staticmethod
    def get_goal_by_id(
        db: Session,
        *,
        goal_id: int,
        user_id: int
    ) -> Goal:
        goal = (
            db.query(Goal)
            .filter(
                Goal.id == goal_id,
                Goal.user_id == user_id,
            )
            .first()
        )

        if not goal:
            raise NoResultFound("Goal not found")

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

        if new_value < 0:
            raise ValueError("Progress value cannot be negative")

        goal.current_value = new_value
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
