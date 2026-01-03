from fastapi import Depends, Header, HTTPException, status, APIRouter
from app.core.config import Settings
from app.db.session import get_db
from app.models.user import User 
from app.core.dependencies import get_current_user
from app.db.seed import seed_exercises
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

@router.post("/admin/seed/exercises")
def seed_exercises_admin(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    seed_exercises(db)
    return {"status": "ok", "message": "Exercises seeded"}
