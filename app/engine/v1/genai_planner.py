from typing import List, Dict
from google import genai
from google.genai import types
from app.engine.v1.schemas import PlannedSessionAI
from app.engine.v1.prompt_builder_lite import build_prompt_lite
from app.core.config import Settings
from pydantic import ValidationError

settings = Settings()
# Only run this block for Gemini Developer API
client = genai.Client(api_key=settings.GEMINI_API_KEY)

import json
import re

def extract_json_from_gemini(response) -> dict:
    try:
        text = response.candidates[0].content.parts[0].text
    except (IndexError, AttributeError):
        raise ValueError("Invalid Gemini response structure")

    # Remove ```json ... ``` or ``` ... ```
    cleaned = re.sub(r"```(?:json)?", "", text).strip()
    cleaned = cleaned.replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode JSON: {e}")


def generate_next_session_genai(
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
    prompt = build_prompt_lite(
        is_first_session=is_first_session,
        previous_sessions_count=previous_sessions_count,
        user_profile=user_profile,
        goal=goal,
        previous_two_sessions=previous_two_sessions,
        last_session_feedback=last_session_feedback,
        exercise_catalog=exercise_catalog,
    )

    # Call Gemini API
    response = client.models.generate_content(
    model='gemini-2.5-flash-lite',
    contents={'text': prompt},
    config={
        'temperature': 0,
        'top_p': 0.95,
        'top_k': 20,
    },
)
    settings.logger.info("AI response received for next session generation.")
    settings.logger.debug(f"AI Response: {response}")
    try:
        # Parse AI JSON response
        content = extract_json_from_gemini(response)
        settings.logger.debug(f"Parsed AI Content: {content}")

    except Exception as e:
        raise ValueError(f"Failed to parse AI response: {e}")

    # Validate against PlannedSessionAI schema
    try:
        session_plan = PlannedSessionAI.model_validate(content)
    except ValidationError as e:
        raise ValueError(f"AI response failed schema validation: {e}")

    # --- Business rules enforcement ---
    # Limit number of exercises
    if len(session_plan.exercises) > 7:
        session_plan.exercises = session_plan.exercises[:7]
    if len(session_plan.exercises) < 3:
        raise ValueError("AI generated fewer than 3 exercises, cannot continue.")

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
