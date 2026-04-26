from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileOut
from app.models.profile import Profile
from app.services.profile_service import ProfileService
from app.services.progress_service import auto_update_goal_progress
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(tags=["Profile"])

@router.post("/", response_model=ProfileOut, status_code=status.HTTP_201_CREATED)
def create_profile(
    profile_in: ProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ProfileService(db)
    
    existing = service.get_by_user(current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists for this user"
        )
    
    profile = service.create(current_user.id, profile_in)
    return profile

@router.get("/", response_model=ProfileOut)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ProfileService(db)
    profile = service.get_by_user(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile

@router.put("/", response_model=ProfileOut)
def update_profile(
    updates: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ProfileService(db)
    profile = service.get_by_user(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    updated_profile = service.update(profile, updates)

    # If weight changed, auto-update any active WeightLoss goal
    if updates.weight is not None:
        auto_update_goal_progress(db, user_id=current_user.id)

    return updated_profile
