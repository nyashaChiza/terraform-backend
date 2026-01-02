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
    # Minimal previous sessions info
    lite_sessions = [
        {
            "session_index": s.get("session_index"),
            "exercise_ids": [e["exercise_id"] for e in s.get("exercises", [])]
        }
        for s in previous_two_sessions
    ]

    # Minimal exercise catalog
    lite_exercises = [
        {"exercise_id": e["exercise_id"], "name": e["name"], "primary_muscle": e["primary_muscle"]}
        for e in exercise_catalog
    ]

    # Minimal last session feedback
    lite_feedback = {
        "effort_rating": last_session_feedback.get("effort_rating"),
        "energy_level": last_session_feedback.get("energy_level"),
        "high_soreness_muscles": [
            m for m, s in last_session_feedback.get("soreness_per_muscle", {}).items() if s >= 7
        ],
        "joint_pain": last_session_feedback.get("joint_pain", False),
    }

    return (
        f"You are a gym coach.\n"
        f"Task: generate the NEXT workout session and give feedback on overall goal progress limit this to 60 characters.\n\n"
        f"User Profile: {json.dumps(user_profile, separators=(',', ':'))}\n"
        f"Goal: {json.dumps(goal, separators=(',', ':'))}\n"
        f"Training Context: {{'is_first_session': {is_first_session}, 'previous_sessions_count': {previous_sessions_count}}}\n"
        f"Previous Sessions (lite): {json.dumps(lite_sessions, separators=(',', ':'))}\n"
        f"Last Session Feedback (lite): {json.dumps(lite_feedback, separators=(',', ':'))}\n"
        f"Available Exercises (lite): {json.dumps(lite_exercises, separators=(',', ':'))}\n"
        f"Rules:\n"
        f"- Follow goal and training level\n"
        f"- If is_first_session, start balanced full-body, conservative volume\n"
        f"- Do NOT invent exercises\n"
        f"- Avoid repeating identical workouts unless first session\n"
        f"- Number of suggested exercises should NEVER exceed 6, sets 10-15, duration 60-90 min\n"
        f"- Intensity: deload/progression/normal based on recovery and energy\n"
        f"Output ONLY valid JSON matching the schema: summary(limit to 60 characters), goal_progress_feedback, estimated_duration_minutes, intensity, exercises (with exercise_id, name, primary_muscle, sets, reps, rest_seconds, notes)"
    )
