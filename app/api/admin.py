from fastapi import Depends, Header, HTTPException, status, APIRouter
from app.core.config import Settings
from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.db.seed import seed_exercises
from app.schemas.user import AdminPasswordReset, UserOut
from sqlalchemy.orm import Session

settings = Settings()

def require_admin(
    x_admin_action_key: str = Header(..., alias="X-Admin-Action-Key"),
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    if x_admin_action_key != settings.ADMIN_ACTION_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin action key",
        )

    return current_user


router = APIRouter(
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
)

@router.post("/seed/exercises")
def seed_exercises_admin(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    seed_exercises(db)
    return {"status": "ok", "message": "Exercises seeded"}


@router.post("/users/{user_id}/reset-password", response_model=UserOut)
def admin_reset_user_password(
    user_id: int,
    payload: AdminPasswordReset,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    Admin resets a user's password to a temporary value.
    The user should change it on next login via /auth/change-password.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.password = hash_password(payload.new_password)
    db.commit()
    db.refresh(user)
    return user
