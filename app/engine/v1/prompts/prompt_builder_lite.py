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

    return (
        "You are a professional gym coach generating workout plans for a fitness app.\n\n"
        "TASK:\n"
        "- Generate the NEXT workout session\n"
        "- Provide short feedback on goal progress (max 90 characters)\n"
        "- Suggest a weight for each exercise based on last session weights and progressive overload principles\n\n"
        f"USER_PROFILE: {json.dumps(user_profile, separators=(',', ':'))}\n"
        f"GOAL: {json.dumps(goal, separators=(',', ':'))}\n"
        f"TRAINING_CONTEXT: {{\"is_first_session\":{str(is_first_session).lower()},"
        f"\"previous_sessions_count\":{previous_sessions_count}}}\n"
        f"PREVIOUS_SESSIONS: {json.dumps(lite_sessions, separators=(',', ':'))}\n"
        f"LAST_FEEDBACK: {json.dumps(lite_feedback, separators=(',', ':'))}\n"
        f"AVAILABLE_EXERCISES: {json.dumps(lite_exercises, separators=(',', ':'))}\n\n"
        "STRICT RULES (DO NOT BREAK):\n"
        "- Output MUST be raw JSON, no markdown, no code blocks\n"
        "- Use ONLY exercises from AVAILABLE_EXERCISES\n"
        "- Field name MUST be 'muscle_group' (never 'primary_muscle')\n"
        "- reps MUST be a single integer greater than 0 and less than 20 (e.g. 10). NEVER use ranges like 8-12\n"
        "- Do NOT invent fields or rename fields\n"
        "- Use 6 exercises exactly\n"
        "- Total sets must be between 10 and 15\n"
        "- Duration must be between 60 and 90 minutes\n"
        "- suggested_weight_kg MUST always be a number (never null). Use 0 for bodyweight exercises\n"
        "- Weight progression: if effort_rating <= 3 increase by 2.5-5kg; if effort_rating == 4 keep same; if effort_rating == 5 decrease by 2.5-5kg\n"
        "- For first session or exercises with no prior weight, estimate from user weight, height, and training_level\n"
        "- notes must be a short form tip (max 60 chars). Do NOT mention weight in notes — weight goes in suggested_weight_kg only\n\n"
        "OUTPUT JSON SCHEMA (MUST MATCH EXACTLY):\n"
        "{"
        "\"title\":\"string (<=40 chars)\","
        "\"summary\":\"string (<=90 chars)\","
        "\"goal_progress_feedback\":\"string (<=90 chars)\","
        "\"estimated_duration_minutes\":number,"
        "\"intensity\":\"Deload|Normal|Progression\","
        "\"exercises\":["
        "{"
        "\"exercise_id\":number,"
        "\"name\":\"string\","
        "\"muscle_group\":\"string\","
        "\"sets\":number,"
        "\"reps\":number,"
        "\"rest_seconds\":number,"
        "\"notes\":\"string or null\","
        "\"suggested_weight_kg\":number"
        "}"
        "]"
        "}\n"
    )
