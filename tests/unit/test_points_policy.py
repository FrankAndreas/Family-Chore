"""
Unit tests for the pure PointsPolicy calculation module.

These tests require NO database — they verify the stateless math directly.
"""
import pytest
from backend.services.points_policy import (
    calculate_points,
    calculate_streak_bonus,
    PointsBreakdown,
    DAILY_BONUS_POINTS,
    STREAK_BONUS_CAP,
    STREAK_BONUS_PER_DAY,
)


# ─── calculate_streak_bonus ────────────────────────────────────────

class TestCalculateStreakBonus:
    def test_streak_zero(self):
        """No streak → 0 bonus."""
        assert calculate_streak_bonus(0) == 0.0

    def test_streak_day_one(self):
        """First day of streak → 0 bonus (ramp starts on day 2)."""
        assert calculate_streak_bonus(1) == 0.0

    def test_streak_day_two(self):
        """Day 2 → +0.1."""
        assert calculate_streak_bonus(2) == pytest.approx(0.1)

    def test_streak_day_three(self):
        """Day 3 → +0.2."""
        assert calculate_streak_bonus(3) == pytest.approx(0.2)

    def test_streak_caps_at_day_six(self):
        """Day 6 → +0.5 (cap)."""
        assert calculate_streak_bonus(6) == pytest.approx(STREAK_BONUS_CAP)

    def test_streak_beyond_cap(self):
        """Day 10 → still +0.5 (capped)."""
        assert calculate_streak_bonus(10) == pytest.approx(STREAK_BONUS_CAP)


# ─── calculate_points ──────────────────────────────────────────────

class TestCalculatePoints:
    """Verify the full points breakdown for various scenarios."""

    def test_first_task_no_streak(self):
        """First task of day, no prior streak → base*mult + daily_bonus."""
        result = calculate_points(
            base_points=100, role_multiplier=1.5,
            current_streak=1, is_first_task_today=True,
        )
        assert isinstance(result, PointsBreakdown)
        assert result.base_points == 100
        assert result.role_multiplier == 1.5
        assert result.streak_bonus == 0.0
        assert result.effective_multiplier == 1.5
        assert result.daily_bonus == DAILY_BONUS_POINTS
        assert result.total_awarded == 155  # int(100 * 1.5) + 5
        assert "(+5 Daily Bonus)" in result.description_suffix
        assert "Streak" not in result.description_suffix

    def test_second_task_same_day(self):
        """Second task same day → no daily bonus."""
        result = calculate_points(
            base_points=100, role_multiplier=1.5,
            current_streak=1, is_first_task_today=False,
        )
        assert result.daily_bonus == 0
        assert result.total_awarded == 150  # int(100 * 1.5) + 0
        assert result.description_suffix == ""

    def test_streak_day_three_with_daily_bonus(self):
        """Day 3 streak + first task → streak bonus + daily bonus."""
        result = calculate_points(
            base_points=100, role_multiplier=1.5,
            current_streak=3, is_first_task_today=True,
        )
        assert result.streak_bonus == pytest.approx(0.2)
        assert result.effective_multiplier == pytest.approx(1.7)
        assert result.daily_bonus == DAILY_BONUS_POINTS
        assert result.total_awarded == 175  # int(100 * 1.7) + 5
        assert "(+5 Daily Bonus)" in result.description_suffix
        assert "[Streak: 3 days]" in result.description_suffix

    def test_streak_capped_at_max(self):
        """Day 7 streak → bonus capped at 0.5."""
        result = calculate_points(
            base_points=100, role_multiplier=1.5,
            current_streak=7, is_first_task_today=True,
        )
        assert result.streak_bonus == pytest.approx(STREAK_BONUS_CAP)
        assert result.effective_multiplier == pytest.approx(2.0)
        assert result.total_awarded == 205  # int(100 * 2.0) + 5

    def test_admin_role_multiplier(self):
        """Admin role (1.0x) with no streak → base + daily bonus."""
        result = calculate_points(
            base_points=50, role_multiplier=1.0,
            current_streak=1, is_first_task_today=True,
        )
        assert result.total_awarded == 55  # int(50 * 1.0) + 5

    def test_teenager_role_multiplier(self):
        """Teenager role (1.2x) with day 2 streak."""
        result = calculate_points(
            base_points=100, role_multiplier=1.2,
            current_streak=2, is_first_task_today=True,
        )
        assert result.streak_bonus == pytest.approx(0.1)
        assert result.effective_multiplier == pytest.approx(1.3)
        assert result.total_awarded == 135  # int(100 * 1.3) + 5

    def test_frozen_dataclass(self):
        """PointsBreakdown should be immutable."""
        result = calculate_points(
            base_points=100, role_multiplier=1.0,
            current_streak=1, is_first_task_today=True,
        )
        with pytest.raises(AttributeError):
            result.total_awarded = 999  # type: ignore[misc]

    def test_constants_exposed(self):
        """Verify configuration constants are accessible for external use."""
        assert DAILY_BONUS_POINTS == 5
        assert STREAK_BONUS_PER_DAY == pytest.approx(0.1)
        assert STREAK_BONUS_CAP == pytest.approx(0.5)
