# app/services/exercise_service.py
from sqlalchemy.orm import Session
from app.models.exercise import Exercise
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate


def get_exercises(db: Session):
    return db.query(Exercise).order_by(Exercise.name).all()


def get_exercise(db: Session, exercise_id: int):
    return db.query(Exercise).filter(Exercise.id == exercise_id).first()


def create_exercise(db: Session, data: ExerciseCreate):
    exercise = Exercise(**data.model_dump())
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


def update_exercise(db: Session, exercise: Exercise, data: ExerciseUpdate):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(exercise, field, value)

    db.commit()
    db.refresh(exercise)
    return exercise


def delete_exercise(db: Session, exercise: Exercise):
    db.delete(exercise)
    db.commit()
