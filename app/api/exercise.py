# app/api/admin/exercises.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.exercise import (
    ExerciseCreate,
    ExerciseUpdate,
    ExerciseOut,
)
from app.services.exercise_service import (
    get_exercises,
    get_exercise,
    create_exercise,
    update_exercise,
    delete_exercise,
)

router = APIRouter(tags=["Admin Exercises"])


@router.get("", response_model=list[ExerciseOut])
def list_exercises(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_exercises(db)


@router.get("/{exercise_id}", response_model=ExerciseOut)
def get_one(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exercise = get_exercise(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise


@router.post(
    "",
    response_model=ExerciseOut,
    status_code=status.HTTP_201_CREATED,
)
def create(
    payload: ExerciseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_exercise(db, payload)


@router.patch("/{exercise_id}", response_model=ExerciseOut)
def update(
    exercise_id: int,
    payload: ExerciseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exercise = get_exercise(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    return update_exercise(db, exercise, payload)


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exercise = get_exercise(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    delete_exercise(db, exercise)
