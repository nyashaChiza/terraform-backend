from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.core.cloudinary import upload_profile_picture, delete_profile_picture
from app.models.user import User
from app.schemas.user import UserOut, UsernameUpdate, DiscoverabilityUpdate, PublicUserOut

router = APIRouter(tags=["Users"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/me/profile-picture", response_model=UserOut)
async def upload_profile_picture_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload or replace the current user's profile picture.

    Accepts JPEG, PNG, or WEBP up to 5 MB.
    The image is stored in Cloudinary; only the URL is saved to the database.
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG, and WEBP images are accepted.",
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image must be under 5 MB.",
        )

    try:
        url = upload_profile_picture(file_bytes, current_user.id)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Image upload failed: {exc}",
        )

    current_user.profile_picture_url = url
    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/me/profile-picture", status_code=204)
def remove_profile_picture(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete the current user's profile picture from Cloudinary and clear the URL."""
    if not current_user.profile_picture_url:
        raise HTTPException(status_code=404, detail="No profile picture to delete.")

    try:
        delete_profile_picture(current_user.id)
    except Exception:
        # If Cloudinary delete fails, still clear the DB URL so the user isn't stuck
        pass

    current_user.profile_picture_url = None
    db.commit()


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's account info."""
    return current_user


@router.patch("/me/username", response_model=UserOut)
def update_username(
    payload: UsernameUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change the current user's display username. Must be unique."""
    existing = db.query(User).filter(
        User.username == payload.username,
        User.id != current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already taken")
    current_user.username = payload.username
    db.commit()
    db.refresh(current_user)
    return current_user


@router.patch("/me/discoverability", response_model=UserOut)
def update_discoverability(
    payload: DiscoverabilityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle whether other users can find this user in the discovery search."""
    current_user.is_discoverable = payload.is_discoverable
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/search", response_model=List[PublicUserOut])
def search_users(
    q: str = Query(..., min_length=2, max_length=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search for discoverable users by username prefix.
    Returns up to 20 results, excluding the calling user.
    """
    # Escape SQL LIKE wildcards (% and _) and the escape char itself so a user
    # searching for "%" doesn't match every username. SQLAlchemy params the
    # value safely against injection, but the wildcards themselves still apply.
    escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    results = (
        db.query(User)
        .filter(
            User.username.ilike(f"{escaped}%", escape="\\"),
            User.is_discoverable == True,
            User.id != current_user.id,
        )
        .limit(20)
        .all()
    )
    return results
