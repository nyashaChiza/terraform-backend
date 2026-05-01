from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.stats_service import StatsService

router = APIRouter(tags=["Stats"])


@router.get("/summary")
def get_stats_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns aggregated stats for the current user:
    - total_sessions: all-time completed sessions
    - streak: consecutive days with a completed session
    - sessions_this_week: sessions completed this calendar week
    - weekly_counts: 8-week bar chart data [{label, count}]
    - personal_records: max weight per exercise [{name, weight_kg, exercise_id}]
    - total_prs: count of exercises with a recorded PR
    """
    return StatsService.get_summary(db=db, user_id=current_user.id)
