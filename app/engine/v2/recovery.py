from typing import Dict


FatigueState = Dict[str, float]


def accumulate_fatigue(
    fatigue: FatigueState,
    activation: Dict[str, float],
    sets: int,
    load_factor: float = 1.0,
) -> FatigueState:
    updated = fatigue.copy()

    for muscle, weight in activation.items():
        updated[muscle] = updated.get(muscle, 0.0) + (sets * weight * load_factor)

    return updated


def decay_fatigue(
    fatigue: FatigueState,
    days_passed: int,
    decay_rate: float = 0.15,
) -> FatigueState:
    return {
        muscle: max(0.0, value - days_passed * decay_rate)
        for muscle, value in fatigue.items()
    }


def fatigue_penalty(
    fatigue: FatigueState,
    activation: Dict[str, float],
) -> float:
    return sum(fatigue.get(m, 0.0) * w for m, w in activation.items())
