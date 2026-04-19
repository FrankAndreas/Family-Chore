"""
Pure, stateless point-calculation policy for the gamification engine.

This module contains NO database access, NO ORM imports, and NO side effects.
It receives primitive values and returns an immutable PointsBreakdown dataclass.

Extending gamification rules (e.g. weekend bonuses, tier multipliers) should
be done here — without touching persistence or orchestration code.
"""
from dataclasses import dataclass


# ─── Configuration Constants ───────────────────────────────────────
DAILY_BONUS_POINTS: int = 5
STREAK_BONUS_PER_DAY: float = 0.1
STREAK_BONUS_CAP: float = 0.5


@dataclass(frozen=True)
class PointsBreakdown:
    """Immutable result of a points calculation."""
    base_points: int
    role_multiplier: float
    streak_bonus: float
    effective_multiplier: float
    daily_bonus: int
    total_awarded: int
    description_suffix: str


def calculate_streak_bonus(current_streak: int) -> float:
    """
    Calculate the streak multiplier bonus.

    Streak bonus ramps +0.1 per consecutive day past the first, capped at +0.5.
    Day 1 → 0.0, Day 2 → 0.1, Day 3 → 0.2, … Day 6+ → 0.5
    """
    return min(STREAK_BONUS_CAP, max(0, current_streak - 1) * STREAK_BONUS_PER_DAY)


def calculate_points(
    base_points: int,
    role_multiplier: float,
    current_streak: int,
    is_first_task_today: bool,
) -> PointsBreakdown:
    """
    Pure function: compute awarded points from base values.

    Args:
        base_points: The task's base point value.
        role_multiplier: The user's role multiplier (e.g. 1.5 for Child).
        current_streak: The user's current consecutive-day streak count.
        is_first_task_today: Whether this is the user's first task completion today.

    Returns:
        An immutable PointsBreakdown with all calculation details.
    """
    daily_bonus = DAILY_BONUS_POINTS if is_first_task_today else 0
    streak_bonus = calculate_streak_bonus(current_streak)
    effective_multiplier = role_multiplier + streak_bonus
    total = int(base_points * effective_multiplier) + daily_bonus

    # Build description suffix
    parts: list[str] = []
    if daily_bonus > 0:
        parts.append(f"(+{daily_bonus} Daily Bonus)")
    if streak_bonus > 0.0:
        parts.append(f"[Streak: {current_streak} days]")
    suffix = " ".join(parts)

    return PointsBreakdown(
        base_points=base_points,
        role_multiplier=role_multiplier,
        streak_bonus=streak_bonus,
        effective_multiplier=effective_multiplier,
        daily_bonus=daily_bonus,
        total_awarded=total,
        description_suffix=suffix,
    )
