from sqlalchemy.orm import Session
from app.models.exercise import Exercise
from app.models.equipment import Equipment
from app.seed_data.exercises import EXERCISE_SEED_DATA
from app.seed_data.equipment import EQUIPMENT_SEED_DATA


def seed_exercises(db: Session) -> None:
    """Seeds the exercises table if empty. Idempotent."""
    if db.query(Exercise).count() > 0:
        return
    db.bulk_save_objects([Exercise(**data) for data in EXERCISE_SEED_DATA])
    db.commit()


def seed_equipment(db: Session) -> None:
    """Seeds the equipment catalog if empty. Idempotent."""
    if db.query(Equipment).count() > 0:
        return
    db.bulk_save_objects([Equipment(**data) for data in EQUIPMENT_SEED_DATA])
    db.commit()
