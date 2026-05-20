import random
import string
from fastapi import APIRouter, Depends, HTTPException, Request, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.session import get_db

from app.models.user import User
from app.models.photo import ProgressPhoto
from app.models.exercise import Exercise
from app.models.goal import Goal
from app.models.profile import Profile
from app.models.session import Session as WorkoutSession


from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.core.dependencies import get_current_user
from app.core.config import get_settings
from app.schemas.user import UserCreate, UserOut, PasswordChange

settings = get_settings()
router = APIRouter(tags=["Auth"])
limiter = Limiter(key_func=get_remote_address)


def _generate_username(email: str, db: Session) -> str:
    """
    Derive a unique username from the email prefix.
    e.g. nyasha@gmail.com → 'nyasha'
    On collision append a short random hex suffix: 'nyasha_4f2'
    """
    base = email.split("@")[0].lower()
    # Strip anything that's not alphanumeric or underscore
    base = "".join(c if c.isalnum() or c == "_" else "_" for c in base)
    candidate = base
    while db.query(User).filter(User.username == candidate).first():
        suffix = "".join(random.choices(string.hexdigits[:16], k=3)).lower()
        candidate = f"{base}_{suffix}"
    return candidate

# -------------------------------
# Register
# -------------------------------
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def register(request: Request, user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    user = User(
        email=user_in.email,
        username=_generate_username(user_in.email, db),
        password=hash_password(user_in.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

# -------------------------------
# Login
# -------------------------------
@router.post("/login")
@limiter.limit("20/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Login is always by email — form_data.username contains the email address
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    refresh_token = create_refresh_token(
        subject=str(user.id),
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# -------------------------------
# Refresh
# -------------------------------
@router.post("/refresh")
@limiter.limit("30/minute")
def refresh_token(request: Request, refresh_token: str = Form(...), db: Session = Depends(get_db)):
    payload = decode_refresh_token(refresh_token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = db.query(User).filter(User.id == user_id_int).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists"
        )

    new_access_token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    new_refresh_token = create_refresh_token(
        subject=str(user.id),
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


# -------------------------------
# Change Password (self-service)
# -------------------------------
@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    current_user.password = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password updated successfully"}


# -------------------------------
# Delete Account
# -------------------------------
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Permanently deletes the authenticated user's account and all associated data:
    progress photos, goals, workout sessions (+ exercises & feedback), profile, and the user record.
    This action is irreversible.
    """
    user_id = current_user.id

    # 1. Progress photos (FK → users.id AND goals.id — must go before goals)
    db.query(ProgressPhoto).filter(ProgressPhoto.user_id == user_id).delete(synchronize_session=False)

    # 2. Goals (FK → users.id)
    db.query(Goal).filter(Goal.user_id == user_id).delete(synchronize_session=False)

    # 3. Sessions — DB cascade handles session_exercises + session_feedbacks
    db.query(WorkoutSession).filter(WorkoutSession.user_id == user_id).delete(synchronize_session=False)

    # 4. Profile (FK → users.id)
    db.query(Profile).filter(Profile.user_id == user_id).delete(synchronize_session=False)

    # 5. User record
    db.delete(current_user)
    db.commit()
