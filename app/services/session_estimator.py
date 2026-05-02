"""
Estimates the number of workout sessions required to achieve a goal.

Called once when a goal is created. The result is stored as
Goal.target_sessions and is never exposed to the client — it is
used solely to calculate a progress percentage.
"""

from __future__ import annotations

import logging
from datetime import date
from math import ceil

from google import genai
from app.core.config import Settings

settings = Settings()
logger = logging.getLogger(__name__)

# Client is constructed lazily inside estimate_sessions() so a missing
# GEMINI_API_KEY in the environment never crashes the server on startup.

_PROMPT_TEMPLATE = """
You are a fitness coach. Given the details below, estimate the total number
of workout sessions a person needs to complete in order to achieve their goal.

Reply with a single integer and nothing else — no explanation, no units, just the number.

Goal type: {goal_type}
Goal description: {description}
Start date: {start_date}
Target date: {due_date}
Days available: {days}

User profile:
- Age: {age}
- Weight: {weight_kg} kg
- Height: {height_cm} cm
- Gender: {gender}
- Experience level: {experience}
- Preferred sessions per week: {sessions_per_week}
""".strip()


def _fallback(preferred_per_week: int | None, start: date, due: date) -> int:
    """Simple maths fallback if Gemini fails."""
    spw = preferred_per_week or 3
    days = (due - start).days
    weeks = max(days / 7, 1)
    return max(ceil(weeks * spw), 4)


def _age_from_dob(dob) -> int | None:
    if dob is None:
        return None
    today = date.today()
    try:
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except Exception:
        return None


def estimate_sessions(*, goal, profile) -> int:
    """
    Ask Gemini how many sessions are needed for this goal.

    Parameters
    ----------
    goal    : Goal ORM instance (type, description, start_date, due_date)
    profile : Profile ORM instance (or None)

    Returns
    -------
    int — estimated session count, minimum 4
    """
    start: date = goal.start_date.date() if hasattr(goal.start_date, "date") else goal.start_date
    due:   date = goal.due_date.date()   if hasattr(goal.due_date,   "date") else goal.due_date
    days = max((due - start).days, 1)

    spw = (profile.preferred_sessions_per_week if profile else None) or 3

    try:
        prompt = _PROMPT_TEMPLATE.format(
            goal_type=goal.type.value if hasattr(goal.type, "value") else str(goal.type),
            description=goal.description or "Not specified",
            start_date=start.isoformat(),
            due_date=due.isoformat(),
            days=days,
            age=_age_from_dob(profile.date_of_birth if profile else None) or "unknown",
            weight_kg=profile.weight if profile else "unknown",
            height_cm=profile.height if profile else "unknown",
            gender=profile.gender.value if (profile and profile.gender) else "unknown",
            experience=profile.experience_level.value if (profile and profile.experience_level) else "unknown",
            sessions_per_week=spw,
        )

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents={"text": prompt},
            config={"temperature": 0},
        )

        raw = response.candidates[0].content.parts[0].text.strip()
        estimate = int("".join(filter(str.isdigit, raw)))
        estimate = max(estimate, 4)
        logger.info("Gemini estimated %d sessions for goal %s", estimate, goal.id)
        return estimate

    except Exception as exc:
        logger.warning("Gemini session estimate failed (%s); using fallback", exc)
        return _fallback(spw, start, due)
