from datetime import date
from typing import Dict, List, Optional
from enum import Enum


class TrainingLevel(str, Enum):
    beginner = "Beginner"
    intermediate = "Intermediate"
    advanced = "Advanced"


class GoalType(str, Enum):
    weight_loss = "WeightLoss"
    muscle_gain = "MuscleGain"
    endurance = "Endurance"
    strength = "Strength"
    custom = "Custom"


def exercise(
    *,
    exercise_id: int,
    name: str,
    muscle_group: str,
    sets: int,
    reps: int,
    rest_seconds: int,
    weight: Optional[float] = None,
    notes: Optional[str] = None,
) -> Dict:
    return {
        "exercise_id": exercise_id,
        "name": name,
        "muscle_group": muscle_group,
        "sets": sets,
        "reps": reps,
        "rest_seconds": rest_seconds,
        "weight": weight,
        "notes": notes
    }

def generate_planned_session(
    *,
    goal_type: GoalType,
    training_level: TrainingLevel,
    session_index: int,
    frequency_per_week: int,
    previous_feedback: Optional[Dict] = None,
) -> Dict:
    """
    Generates a workout plan payload.

    session_index: starts at 1 and increments per goal
    """

    base_volume = _volume_by_level(training_level)
    intensity_modifier = _feedback_modifier(previous_feedback)

    exercises = _select_exercises(
        goal_type=goal_type,
        volume=base_volume,
        intensity_modifier=intensity_modifier,
        session_index=session_index,
    )

    estimated_duration = _estimate_duration(exercises)

    return {
        "version": "1.0",
        "goal_type": goal_type.value,
        "training_level": training_level.value,
        "session_index": session_index,
        "estimated_duration_minutes": estimated_duration,
        "exercises": exercises,
    }

def generate_planned_session(
    *,
    goal_type: GoalType,
    training_level: TrainingLevel,
    session_index: int,
    frequency_per_week: int,
    previous_feedback: Optional[Dict] = None,
) -> Dict:
    """
    Generates a workout plan payload.

    session_index: starts at 1 and increments per goal
    """

    base_volume = _volume_by_level(training_level)
    intensity_modifier = _feedback_modifier(previous_feedback)

    exercises = _select_exercises(
        goal_type=goal_type,
        base_volume=base_volume,
        intensity_modifier=intensity_modifier,
        # session_index=session_index,
    )

    estimated_duration = _estimate_duration(exercises)

    return {
        "version": "1.0",
        "goal_type": goal_type.value,
        "training_level": training_level.value,
        "session_index": session_index,
        "estimated_duration_minutes": estimated_duration,
        "exercises": exercises,
    }

def _volume_by_level(level: TrainingLevel) -> int:
    return {
        TrainingLevel.beginner: 2,
        TrainingLevel.intermediate: 3,
        TrainingLevel.advanced: 4,
    }[level]


def _feedback_modifier(previous_feedback: Optional[Dict]) -> float:
    if not previous_feedback:
        return 1.0

    effort = previous_feedback.get("effort_rating", 5)
    energy = previous_feedback.get("energy_level", 5)

    if effort >= 8 and energy <= 3:
        return 0.8  # deload
    if effort <= 5 and energy >= 7:
        return 1.1  # progression

    return 1.0

def _select_exercises(
    *,
    goal_type: GoalType,
    base_volume: int,
    intensity_modifier: float,
) -> list[dict]:
    """
    Returns a balanced full-body session.
    Exercises are grouped by movement pattern, not by name.
    """

    def scaled_sets(multiplier: float = 1.0) -> int:
        return max(1, round(base_volume * multiplier * intensity_modifier))

    exercises: list[dict] = []

    # --------------------
    # Cardio (warm-up)
    # --------------------
    exercises.append(
        exercise(
            exercise_id=1,
            name="Stationary Bike",
            muscle_group="Cardio",
            sets=1,
            reps=1,
            rest_seconds=0,
            notes="5–10 min warm-up or cool-down",
        )
    )

    # --------------------
    # Legs (compound)
    # --------------------
    exercises.append(
        exercise(
            exercise_id=2,
            name="Leg Press",
            muscle_group="Legs",
            sets=scaled_sets(1.2),
            reps=10,
            rest_seconds=120,
        )
    )

    # --------------------
    # Back (vertical pull)
    # --------------------
    exercises.append(
        exercise(
            exercise_id=3,
            name="Lat Pulldown",
            muscle_group="Back",
            sets=scaled_sets(),
            reps=10,
            rest_seconds=90,
        )
    )

    # --------------------
    # Back (horizontal pull)
    # --------------------
    exercises.append(
        exercise(
            exercise_id=4,
            name="Seated Cable Row",
            muscle_group="Back",
            sets=scaled_sets(),
            reps=10,
            rest_seconds=90,
        )
    )

    # --------------------
    # Chest (press)
    # --------------------
    exercises.append(
        exercise(
            exercise_id=5,
            name="Chest Press (Machine)",
            muscle_group="Chest",
            sets=scaled_sets(),
            reps=8 if goal_type == GoalType.strength else 10,
            rest_seconds=120,
        )
    )

    # --------------------
    # Chest (fly)
    # --------------------
    exercises.append(
        exercise(
            exercise_id=6,
            name="Pec Fly (Machine)",
            muscle_group="Chest",
            sets=scaled_sets(0.8),
            reps=12,
            rest_seconds=75,
        )
    )

    # --------------------
    # Shoulders
    # --------------------
    exercises.append(
        exercise(
            exercise_id=7,
            name="Shoulder Press (Machine)",
            muscle_group="Shoulders",
            sets=scaled_sets(),
            reps=10,
            rest_seconds=90,
        )
    )

    exercises.append(
        exercise(
            exercise_id=8,
            name="Lateral Raises",
            muscle_group="Shoulders",
            sets=scaled_sets(0.7),
            reps=15,
            rest_seconds=60,
        )
    )

    # --------------------
    # Arms – Biceps
    # --------------------
    exercises.append(
        exercise(
            exercise_id=9,
            name="Bicep Curls (Machine/Cable)",
            muscle_group="Biceps",
            sets=scaled_sets(0.7),
            reps=12,
            rest_seconds=60,
        )
    )

    # --------------------
    # Arms – Triceps
    # --------------------
    exercises.append(
        exercise(
            exercise_id=10,
            name="Tricep Pushdown (Cable)",
            muscle_group="Triceps",
            sets=scaled_sets(0.7),
            reps=12,
            rest_seconds=60,
        )
    )

    exercises.append(
        exercise(
            exercise_id=11,
            name="Lat Pulldown (Triceps Extension)",
            muscle_group="Triceps",
            sets=scaled_sets(0.6),
            reps=12,
            rest_seconds=60,
            notes="Use triceps attachment",
        )
    )

    # --------------------
    # Core
    # --------------------
    exercises.append(
        exercise(
            exercise_id=12,
            name="Abdominal Crunch (Machine)",
            muscle_group="Core",
            sets=scaled_sets(1.1),
            reps=15,
            rest_seconds=45,
        )
    )

    return exercises



def _estimate_duration(exercises: List[Dict]) -> int:
    total_sets = sum(e["sets"] for e in exercises)
    avg_set_time = 45  # seconds
    avg_rest = sum(e["rest_seconds"] for e in exercises) / len(exercises)

    total_seconds = total_sets * (avg_set_time + avg_rest)
    return round(total_seconds / 60)


if __name__ == "__main__":
    # Example usage
    planned_session = generate_planned_session(
        goal_type=GoalType.weight_loss,
        training_level=TrainingLevel.intermediate,
        session_index=1,
        frequency_per_week=3,
        previous_feedback={
            "effort_rating": 6,
            "energy_level": 7,
        },
    )
    import pprint
    pprint.pprint(planned_session)