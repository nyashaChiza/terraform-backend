from typing import Dict


def max_sets_for_muscle(
    muscle: str,
    training_level: str,
) -> int:
    caps = {
        "Beginner": 8,
        "Intermediate": 12,
        "Advanced": 16,
    }
    return caps.get(training_level, 10)


def volume_allowed(
    *,
    muscle: str,
    current_volume: int,
    planned_sets: int,
    training_level: str,
) -> bool:
    cap = max_sets_for_muscle(muscle, training_level)
    return (current_volume + planned_sets) <= cap
