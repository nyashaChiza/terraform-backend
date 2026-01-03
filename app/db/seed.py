from sqlalchemy.orm import Session
from app.models.exercise import Exercise
from app.seed_data.exercises import EXERCISE_SEED_DATA


def seed_exercises(db: Session) -> None:
    """
    Seeds the exercises table if empty.
    This function is idempotent and safe to run on startup.
    """

    existing_count = db.query(Exercise).count()

    if existing_count > 0:
        # Table already seeded — do nothing
        return

    exercises = [Exercise(**data) for data in EXERCISE_SEED_DATA]

    db.bulk_save_objects(exercises)
    db.commit()
