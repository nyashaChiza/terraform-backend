import json

def build_prompt_lite(
    *,
    is_first_session: bool,
    previous_sessions_count: int,
    user_profile: dict,
    goal: dict,
    previous_two_sessions: list[dict],
    last_session_feedback: dict,
    exercise_catalog: list[dict],
    available_equipment_categories: list[str] | None = None,
) -> str:
    lite_sessions = [
        {
            "exercise_ids": [e["exercise_id"] for e in s.get("exercises", [])]
        }
        for s in previous_two_sessions
    ]

    lite_exercises = [
        {
            "exercise_id": e["exercise_id"],
            "name": e["name"],
            "muscle_group": e["primary_muscle"],
        }
        for e in exercise_catalog
    ]

    lite_feedback = {
        "summary": last_session_feedback.get("summary"),
        "effort_rating": last_session_feedback.get("effort_rating"),
        "energy_level": last_session_feedback.get("energy_level"),
        "joint_pain": last_session_feedback.get("joint_pain", False),
        "soreness_per_muscle_out_of_5": last_session_feedback.get("soreness_per_muscle", {}),
        "weights_used": last_session_feedback.get("weights_used", []),
    }

    # Trimmed prompt — JSON mode + Pydantic validation handle the strict bits
    # the long "RULES" block used to enforce. This cuts ~400 input tokens which
    # speeds up Gemini and keeps Vercel hobby's 10s function timeout safe.
    return (
        "You are a gym coach generating the next workout session. "
        "Output ONLY valid JSON matching the schema below — no prose, no markdown.\n\n"
        f"USER_PROFILE: {json.dumps(user_profile, separators=(',', ':'))}\n"
        f"GOAL: {json.dumps(goal, separators=(',', ':'))}\n"
        f"CONTEXT: {{\"is_first_session\":{str(is_first_session).lower()},\"prev_count\":{previous_sessions_count}}}\n"
        f"PREVIOUS_SESSIONS: {json.dumps(lite_sessions, separators=(',', ':'))}\n"
        f"LAST_FEEDBACK: {json.dumps(lite_feedback, separators=(',', ':'))}\n"
        f"AVAILABLE_EXERCISES: {json.dumps(lite_exercises, separators=(',', ':'))}\n"
        f"AVAILABLE_EQUIPMENT: {json.dumps(available_equipment_categories or ['bodyweight'], separators=(',', ':'))}\n\n"
        "RULES:\n"
        "- Pick exactly 6 exercises from AVAILABLE_EXERCISES.\n"
        "- Total sets 10-15. Duration 60-90 min. reps is one integer (NOT a range).\n"
        "- For Plank/timed exercises: use reps = duration in seconds.\n"
        "- suggested_weight_kg: number, 0 for bodyweight. Progress weight: effort_rating<=3 +2.5-5kg, ==4 same, ==5 -2.5-5kg.\n"
        "- notes: short tip (<=60 chars), no weight info.\n"
        "- title: name the muscle group/focus of THIS session (e.g. 'Push Day: Chest & Shoulders'). No generic titles.\n\n"
        "SCHEMA:\n"
        '{"title":"<=40 chars","summary":"<=90 chars","goal_progress_feedback":"<=90 chars",'
        '"estimated_duration_minutes":int,"intensity":"Deload|Normal|Progression",'
        '"exercises":[{"exercise_id":int,"name":str,"muscle_group":str,"sets":int,"reps":int,'
        '"rest_seconds":int,"notes":str|null,"suggested_weight_kg":number}]}\n'
    )
