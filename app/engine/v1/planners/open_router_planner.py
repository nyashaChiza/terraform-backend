from openrouter import OpenRouter
from app.core.config import Settings
import json
from app.engine.v1.schemas.schemas import PlannedSessionAI
from app.engine.v1.prompts.prompt_builder_lite import build_prompt_lite

settings = Settings()

def generate_next_session_openrouter(
    *,
    is_first_session: bool,
    previous_sessions_count: int,
    last_session_feedback: dict,
    previous_two_sessions: list[dict],
    user_profile: dict,
    goal: dict,
    exercise_catalog: list[dict],
) -> PlannedSessionAI:

    prompt = build_prompt_lite(
        is_first_session=is_first_session,
        previous_sessions_count=previous_sessions_count,
        user_profile=user_profile,
        goal=goal,
        previous_two_sessions=previous_two_sessions,
        last_session_feedback=last_session_feedback,
        exercise_catalog=exercise_catalog,
    )
    settings.logger.debug(f"OpenRouter Prompt: {prompt}")
    with OpenRouter(api_key=settings.OPENROUTER_API_KEY) as client:
        response = client.chat.send(
            model="minimax/minimax-m2",
            messages=[{"role": "user", "content": prompt}],
        )

    # The actual text content returned by the model
    output_text = response.output_text  # or response.output depending on SDK

    # Parse the JSON returned by the model
    parsed = json.loads(output_text)
    settings.logger.info("AI response received for next session generation.")
    settings.logger.debug(f"AI Response: {parsed}")
    # Validate against your schema
    return PlannedSessionAI.model_validate(parsed)
