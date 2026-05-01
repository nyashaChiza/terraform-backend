from sqlalchemy.orm import Session as DBSession
from datetime import datetime, timezone, timedelta
from typing import Dict, List

from app.models.session import Session as SessionModel, SessionFeedback
from app.models.enums import SessionStatus


class StatsService:

    # ─── public ───────────────────────────────────────────────

    @staticmethod
    def get_summary(db: DBSession, *, user_id: int) -> dict:
        completed = (
            db.query(SessionModel)
            .filter(
                SessionModel.user_id == user_id,
                SessionModel.status == SessionStatus.COMPLETED,
            )
            .order_by(SessionModel.completed_at.desc())
            .all()
        )

        personal_records = StatsService._personal_records(db, user_id=user_id)

        return {
            "total_sessions": len(completed),
            "streak": StatsService._compute_streak(completed),
            "sessions_this_week": StatsService._sessions_this_week(completed),
            "weekly_counts": StatsService._weekly_counts(completed, weeks=8),
            "personal_records": personal_records,
            "total_prs": len(personal_records),
        }

    # ─── helpers ──────────────────────────────────────────────

    @staticmethod
    def _aware(dt: datetime) -> datetime:
        """Ensure datetime is timezone-aware (UTC)."""
        if dt is None:
            return None
        return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)

    @staticmethod
    def _compute_streak(completed_sessions: list) -> int:
        """Count consecutive calendar days (including today) that have ≥1 session."""
        dates = {
            StatsService._aware(s.completed_at).date()
            for s in completed_sessions
            if s.completed_at
        }
        if not dates:
            return 0

        today = datetime.now(timezone.utc).date()
        # Allow streak if today OR yesterday is the most recent session
        check = today if today in dates else today - timedelta(days=1)
        streak = 0
        while check in dates:
            streak += 1
            check -= timedelta(days=1)
        return streak

    @staticmethod
    def _sessions_this_week(completed_sessions: list) -> int:
        now = datetime.now(timezone.utc)
        week_start = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return sum(
            1
            for s in completed_sessions
            if s.completed_at and StatsService._aware(s.completed_at) >= week_start
        )

    @staticmethod
    def _weekly_counts(completed_sessions: list, weeks: int = 8) -> list:
        """Return a list of {label, count} buckets for the last `weeks` weeks."""
        now = datetime.now(timezone.utc)
        result = []
        for i in range(weeks - 1, -1, -1):
            week_end = now - timedelta(weeks=i)
            week_start = week_end - timedelta(weeks=1)
            count = sum(
                1
                for s in completed_sessions
                if s.completed_at
                and week_start <= StatsService._aware(s.completed_at) < week_end
            )
            # Label: short date for recent weeks, "Wn" for older ones
            if i <= 3:
                label = f"{week_end.day} {week_end.strftime('%b')}"
            else:
                label = f"W{weeks - i}"
            result.append({"label": label, "count": count})
        return result

    @staticmethod
    def _personal_records(db: DBSession, *, user_id: int) -> list:
        """Max weight lifted per exercise, derived from session feedback."""
        feedbacks = (
            db.query(SessionFeedback)
            .join(SessionModel, SessionFeedback.session_id == SessionModel.id)
            .filter(SessionModel.user_id == user_id)
            .all()
        )

        records: Dict[str, dict] = {}
        for fb in feedbacks:
            if not fb.weights_used:
                continue
            for entry in fb.weights_used:
                if not isinstance(entry, dict):
                    continue
                name = (entry.get("name") or "").strip()
                weight_kg = entry.get("weight_kg") or 0
                exercise_id = entry.get("exercise_id")
                if name and weight_kg > 0:
                    if name not in records or weight_kg > records[name]["weight_kg"]:
                        records[name] = {
                            "name": name,
                            "weight_kg": weight_kg,
                            "exercise_id": exercise_id,
                        }

        return sorted(records.values(), key=lambda x: x["weight_kg"], reverse=True)
