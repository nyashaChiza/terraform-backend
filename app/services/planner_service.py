
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.session import PlannedSession
from app.models.user import User
from app.models.session import SessionFeedback
from app.engine.v1.openai_planner import generate_next_session_open_ai
from app.engine.v1.open_router_planner import generate_next_session_openrouter 
from app.engine.v1.genai_planner import generate_next_session_genai 
from app.engine.v1.schemas import PlannedSessionAI


class PlannerService:
    """
    Service responsible for generating the next workout session
    using AI and persisting it in the database.
    """

    @staticmethod
    def create_next_planned_session(
        *,
        db: Session,
        user: User,
        goal: Dict,
        exercise_catalog: List[Dict],
        planned_date: Optional[str] = None,
    ) -> PlannedSession:
        """
        1. Fetch user's previous sessions and last session feedback
        2. Call the AI to generate next session plan
        3. Persist the planned session in the DB
        """

        # Fetch previous sessions (most recent first)
        previous_sessions = (
            db.query(PlannedSession)
            .filter(PlannedSession.user_id == user.id)
            .order_by(PlannedSession.planned_date.desc())
            .all()
        )

        # Take last two sessions for context
        previous_two_sessions = [
            ps.plan_payload for ps in previous_sessions[:2]
        ]

        # Fetch feedback from last logged session (if any)
        last_feedback: Optional[Dict] = {}
        if previous_sessions:
            last_logged = (
                db.query(SessionFeedback)
                .join(
                    PlannedSession,
                    SessionFeedback.logged_session_id == PlannedSession.id
                )
                .filter(PlannedSession.user_id == user.id)
                .order_by(SessionFeedback.created.desc())
                .first()
            )

            if last_logged:
                last_feedback = {
                    "soreness_per_muscle": last_logged.soreness_per_muscle or {},
                    "joint_pain": last_logged.joint_pain,
                    "effort_rating": last_logged.effort_rating,
                    "energy_level": last_logged.energy_level,
                }


        # Generate next session using AI
        ai_plan: PlannedSessionAI = generate_next_session_genai(
            user_profile={
                "age": user.age,
                 "weight": user.profile.weight,
                 "height": user.profile.height,
                 "training_level": user.profile.experience_level,
             },
            goal=goal,
            previous_sessions=previous_sessions,
            previous_two_sessions=previous_two_sessions,
            last_session_feedback=last_feedback,
            exercise_catalog=exercise_catalog
        )

        # Persist the planned session
        planned = PlannedSession(
            user_id=user.id,
            planned_date=planned_date,  # optional: could auto-assign to today
            estimated_duration_minutes=ai_plan.estimated_duration_minutes,
            plan_payload=ai_plan.model_dump(),
            summary=ai_plan.summary,
            goal_progress_feedback=ai_plan.goal_progress_feedback,
            intensity=ai_plan.intensity.capitalize()
        )

        db.add(planned)
        db.commit()
        db.refresh(planned)
        return planned
