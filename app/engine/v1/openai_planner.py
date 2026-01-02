from typing import List, Dict
from openai import OpenAI
from app.engine.v1.schemas import PlannedSessionAI
from app.engine.v1.prompt_builder import build_prompt
from app.core.config import Settings
from pydantic import ValidationError

settings = Settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_next_session_open_ai(
    *,
    user_profile: dict,
    goal: dict,
    previous_sessions: List[dict],
    previous_two_sessions: List[dict],
    last_session_feedback: dict,
    exercise_catalog: List[dict],
) -> PlannedSessionAI:
    """
    Generates the next workout session using OpenAI, enforces business rules,
    and validates output against PlannedSessionAI schema.

    Returns a Pydantic model instance.
    """

    is_first_session = len(previous_sessions) == 0
    previous_sessions_count = len(previous_sessions)

    # Build prompt for the AI
    prompt = build_prompt(
        is_first_session=is_first_session,
        previous_sessions_count=previous_sessions_count,
        user_profile=user_profile,
        goal=goal,
        previous_two_sessions=previous_two_sessions,
        last_session_feedback=last_session_feedback,
        exercise_catalog=exercise_catalog,
    )

    # Call OpenAI API
    response = client.responses.create(
        model="gpt-4.1",
        input=prompt,
        temperature=0.4,
    )
    settings.logger.info("AI response received for next session generation.")
    settings.logger.debug(f"AI Response: {response}")
    try:
        # Parse AI JSON response
        content: dict = response.output_parsed
    except Exception as e:
        raise ValueError(f"Failed to parse AI response: {e}")

    # Validate against PlannedSessionAI schema
    try:
        session_plan = PlannedSessionAI.model_validate(content)
    except ValidationError as e:
        raise ValueError(f"AI response failed schema validation: {e}")

    # --- Business rules enforcement ---
    # Limit number of exercises
    if len(session_plan.exercises) > 10:
        session_plan.exercises = session_plan.exercises[:10]
    if len(session_plan.exercises) < 6:
        raise ValueError("AI generated fewer than 6 exercises, cannot continue.")

    # Ensure total working sets within 20–28
    total_sets = sum(ex.sets for ex in session_plan.exercises)
    if total_sets > 28:
        # scale sets proportionally
        scale = 28 / total_sets
        for ex in session_plan.exercises:
            ex.sets = max(1, round(ex.sets * scale))
    elif total_sets < 20:
        # increase sets proportionally if possible
        scale = 20 / total_sets
        for ex in session_plan.exercises:
            ex.sets = max(1, round(ex.sets * scale))

    # Enforce duration 60–90 minutes
    if session_plan.estimated_duration_minutes < 60:
        session_plan.estimated_duration_minutes = 60
    elif session_plan.estimated_duration_minutes > 90:
        session_plan.estimated_duration_minutes = 90

    return session_plan
