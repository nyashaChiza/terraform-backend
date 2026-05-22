from sqlalchemy import func
from sqlalchemy.orm import Session as DBSession
from datetime import datetime, timezone, timedelta
from typing import Dict, List

from app.models.session import Session as SessionModel, SessionFeedback
from app.models.enums import SessionStatus


class StatsService:

    # ─── public ───────────────────────────────────────────────

    @staticmethod
    def get_summary(db: DBSession, *, user_id: int) -> dict:
        """
        Computes all stats for a user using three lightweight queries instead
        of loading full ORM rows. This is significantly faster on cold-start
        Postgres (Neon) and keeps total response time well under Vercel's 10s
        function-timeout limit.
        """

        # 1. Total completed sessions — a single COUNT(*) instead of len(.all())
        total_sessions = (
            db.query(func.count(SessionModel.id))
            .filter(
                SessionModel.user_id == user_id,
                SessionModel.status == SessionStatus.COMPLETED,
            )
            .scalar()
        ) or 0

        # 2. Only fetch the `completed_at` column for streak/weekly/this-week.
        #    Loads a list of datetimes, not full SessionModel objects.
        completed_at_rows = (
            db.query(SessionModel.completed_at)
            .filter(
                SessionModel.user_id == user_id,
                SessionModel.status == SessionStatus.COMPLETED,
                SessionModel.completed_at.isnot(None),
            )
            .order_by(SessionModel.completed_at.desc())
            .all()
        )
        completed_dates: List[datetime] = [row[0] for row in completed_at_rows]

        # 3. Only fetch the `weights_used` JSON column for PRs — skip rows
        #    where it's null at the DB level so we don't pull unused data.
        pr_rows = (
            db.query(SessionFeedback.weights_used)
            .join(SessionModel, SessionFeedback.session_id == SessionModel.id)
            .filter(
                SessionModel.user_id == user_id,
                SessionFeedback.weights_used.isnot(None),
            )
            .all()
        )
        personal_records = StatsService._compute_prs([row[0] for row in pr_rows])

        return {
            "total_sessions": total_sessions,
            "streak": StatsService._compute_streak(completed_dates),
            "sessions_this_week": StatsService._sessions_this_week(completed_dates),
            "weekly_counts": StatsService._weekly_counts(completed_dates, weeks=8),
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
    def _compute_streak(completed_dates: List[datetime]) -> int:
        """Count consecutive calendar days (including today) that have ≥1 session."""
        if not completed_dates:
            return 0

        dates = {StatsService._aware(d).date() for d in completed_dates if d}
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
    def _sessions_this_week(completed_dates: List[datetime]) -> int:
        now = datetime.now(timezone.utc)
        week_start = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return sum(
            1
            for d in completed_dates
            if d and StatsService._aware(d) >= week_start
        )

    @staticmethod
    def _weekly_counts(completed_dates: List[datetime], weeks: int = 8) -> list:
        """Return a list of {label, count} buckets for the last `weeks` weeks."""
        now = datetime.now(timezone.utc)
        # Pre-normalize once instead of inside every loop iteration
        normalized = [StatsService._aware(d) for d in completed_dates if d]
        result = []
        for i in range(weeks - 1, -1, -1):
            week_end = now - timedelta(weeks=i)
            week_start = week_end - timedelta(weeks=1)
            count = sum(1 for d in normalized if week_start <= d < week_end)
            # Label: short date for recent weeks, "Wn" for older ones
            if i <= 3:
                label = f"{week_end.day} {week_end.strftime('%b')}"
            else:
                label = f"W{weeks - i}"
            result.append({"label": label, "count": count})
        return result

    @staticmethod
    def _compute_prs(weights_used_list: List) -> list:
        """Derive max weight lifted per exercise from a list of weights_used JSON."""
        records: Dict[str, dict] = {}
        for weights_used in weights_used_list:
            if not weights_used:
                continue
            for entry in weights_used:
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
