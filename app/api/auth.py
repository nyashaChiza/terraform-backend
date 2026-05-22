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
from app.schemas.user import UserCreate, UserOut, PasswordChange, AccountDelete

settings = get_settings()
router = APIRouter(tags=["Auth"])
limiter = Limiter(key_func=get_remote_address)


def _normalize_email(email: str) -> str:
    """Email comparisons must be case-insensitive — store lowercase."""
    return email.strip().lower()


def _generate_username(email: str, db: Session) -> str:
    """
    Derive a unique username from the email prefix.
    e.g. nyasha@gmail.com → 'nyasha'
    On collision append a short random hex suffix: 'nyasha_4f2'
    Caps the base at 20 chars so usernames stay readable.
    """
    base = email.split("@")[0].lower()
    # Strip anything that's not alphanumeric or underscore
    base = "".join(c if c.isalnum() or c == "_" else "_" for c in base)
    # Cap at 20 chars so display names stay reasonable
    base = base[:20] or "user"
    candidate = base
    while db.query(User).filter(User.username == candidate).first():
        suffix = "".join(random.choices(string.hexdigits[:16], k=3)).lower()
        candidate = f"{base}_{suffix}"
    return candidate


def _issue_tokens(user: User) -> dict:
    """Issue an access + refresh token pair bound to the user's token_version."""
    tv = user.token_version or 0
    access = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_version=tv,
    )
    refresh = create_refresh_token(
        subject=str(user.id),
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_version=tv,
    )
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
    }


# -------------------------------
# Register
# -------------------------------
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def register(request: Request, user_in: UserCreate, db: Session = Depends(get_db)):
    normalized_email = _normalize_email(user_in.email)
    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    user = User(
        email=normalized_email,
        username=_generate_username(normalized_email, db),
        password=hash_password(user_in.password),
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
    normalized_email = _normalize_email(form_data.username)
    user = db.query(User).filter(User.email == normalized_email).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return _issue_tokens(user)

# -------------------------------
# Refresh
# -------------------------------
@router.post("/refresh")
@limiter.limit("30/minute")
def refresh_token(request: Request, refresh_token: str = Form(...), db: Session = Depends(get_db)):
    INVALID = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
    )

    try:
        payload = decode_refresh_token(refresh_token)
    except Exception:
        raise INVALID

    user_id = payload.get("sub")
    if not user_id:
        raise INVALID

    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise INVALID

    user = db.query(User).filter(User.id == user_id_int).first()
    if not user:
        raise INVALID

    # Reject refresh tokens whose token_version is older than the user's current —
    # e.g. password changed or logged out everywhere after this token was issued.
    if payload.get("tv", 0) != (user.token_version or 0):
        raise INVALID

    # Issue a fresh pair (refresh-token rotation).
    # The old refresh token is implicitly still valid until its natural expiry
    # because we use stateless JWTs; if you need *immediate* invalidation of
    # the old token, bump user.token_version here. For now, rotation alone is
    # the standard practice for stateless JWT refresh flows.
    return _issue_tokens(user)


# -------------------------------
# Logout (revokes all outstanding tokens for this user)
# -------------------------------
@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
def logout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Invalidate ALL outstanding access and refresh tokens for the current user
    by bumping their token_version. Useful for "log out everywhere" semantics.
    """
    current_user.token_version = (current_user.token_version or 0) + 1
    db.commit()


# -------------------------------
# Change Password (self-service)
# -------------------------------
@router.post("/change-password", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def change_password(
    request: Request,
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
    # Invalidate all existing tokens — user must sign in again on other devices.
    current_user.token_version = (current_user.token_version or 0) + 1
    db.commit()

    # Issue a new pair so the current device stays logged in seamlessly.
    return {
        "message": "Password updated successfully",
        **_issue_tokens(current_user),
    }


# -------------------------------
# Delete Account (requires password confirmation)
# -------------------------------
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
def delete_account(
    request: Request,
    payload: AccountDelete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Permanently deletes the authenticated user's account and all associated data:
    progress photos, goals, workout sessions (+ exercises & feedback), profile, and the user record.
    Requires the current password to confirm — a stolen token alone is not enough.
    This action is irreversible.
    """
    # Password confirmation — prevents account deletion from a stolen token alone.
    if not verify_password(payload.password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is incorrect",
        )

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
