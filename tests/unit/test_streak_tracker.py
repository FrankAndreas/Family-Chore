"""
Unit tests for the StreakTracker module.

Tests verify streak state-machine transitions at the model level.
Uses DB fixtures because streak_tracker mutates User model objects.
"""
import pytest
from datetime import date, datetime, timezone
from backend.services.streak_tracker import update_user_streak, reset_expired_streaks
from backend import models


# ─── update_user_streak ────────────────────────────────────────────

class TestUpdateUserStreak:
    """Tests for the streak state-machine function."""

    @pytest.fixture
    def user(self, db_session, seeded_db):
        """A fresh Child user with no streak history."""
        user = models.User(
            nickname="StreakKid", login_pin="1234", role_id=4,
            current_points=0, lifetime_points=0,
            current_streak=0, last_task_date=None,
        )
        db_session.add(user)
        db_session.commit()
        return user

    def test_first_ever_task_starts_streak(self, user):
        """First task ever → streak=1, is_first=True."""
        streak, is_first = update_user_streak(user, date(2025, 1, 1))
        assert streak == 1
        assert is_first is True
        assert user.current_streak == 1
        assert user.last_task_date == date(2025, 1, 1)

    def test_second_task_same_day_no_change(self, user):
        """Second task on the same day → streak unchanged, is_first=False."""
        update_user_streak(user, date(2025, 1, 1))
        streak, is_first = update_user_streak(user, date(2025, 1, 1))
        assert streak == 1
        assert is_first is False
        assert user.current_streak == 1

    def test_consecutive_day_increments(self, user):
        """Task on the next day → streak increments."""
        update_user_streak(user, date(2025, 1, 1))
        streak, is_first = update_user_streak(user, date(2025, 1, 2))
        assert streak == 2
        assert is_first is True
        assert user.current_streak == 2

    def test_multi_day_consecutive(self, user):
        """3 consecutive days → streak=3."""
        update_user_streak(user, date(2025, 1, 1))
        update_user_streak(user, date(2025, 1, 2))
        streak, _ = update_user_streak(user, date(2025, 1, 3))
        assert streak == 3

    def test_missed_day_resets_streak(self, user):
        """Skipping a day resets streak to 1."""
        update_user_streak(user, date(2025, 1, 1))
        assert user.current_streak == 1

        # Skip Jan 2 entirely
        streak, is_first = update_user_streak(user, date(2025, 1, 3))
        assert streak == 1
        assert is_first is True

    def test_missed_multiple_days_resets(self, user):
        """Skipping several days still resets to 1."""
        update_user_streak(user, date(2025, 1, 1))
        update_user_streak(user, date(2025, 1, 2))
        assert user.current_streak == 2

        streak, _ = update_user_streak(user, date(2025, 1, 10))
        assert streak == 1

    def test_last_task_date_updates_only_on_first(self, user):
        """last_task_date should only change on the first task of the day."""
        update_user_streak(user, date(2025, 1, 1))
        assert user.last_task_date == date(2025, 1, 1)

        # Second task same day — date stays
        update_user_streak(user, date(2025, 1, 1))
        assert user.last_task_date == date(2025, 1, 1)


# ─── reset_expired_streaks ────────────────────────────────────────

class TestResetExpiredStreaks:
    """Tests for the midnight cron streak-expiry function."""

    @pytest.fixture
    def users(self, db_session, seeded_db):
        """Two users with active streaks."""
        child = models.User(
            nickname="ActiveChild", login_pin="1111", role_id=4,
            current_streak=5, last_task_date=date(2025, 1, 1),
        )
        teen = models.User(
            nickname="StaleTeen", login_pin="2222", role_id=3,
            current_streak=3, last_task_date=date(2024, 12, 31),
        )
        db_session.add_all([child, teen])
        db_session.commit()
        return {"child": child, "teen": teen}

    def test_resets_stale_streak(self, db_session, users):
        """User who last played 2+ days ago gets reset."""
        midnight_jan2 = datetime(2025, 1, 2, 0, 0, tzinfo=timezone.utc)
        count = reset_expired_streaks(db_session, reference_date=midnight_jan2)

        assert count == 1
        db_session.refresh(users["teen"])
        assert users["teen"].current_streak == 0

    def test_preserves_recent_streak(self, db_session, users):
        """User who played yesterday keeps their streak."""
        midnight_jan2 = datetime(2025, 1, 2, 0, 0, tzinfo=timezone.utc)
        reset_expired_streaks(db_session, reference_date=midnight_jan2)

        db_session.refresh(users["child"])
        assert users["child"].current_streak == 5

    def test_no_resets_when_all_active(self, db_session, users):
        """When all users played yesterday, count is 0."""
        # Move teen to yesterday
        users["teen"].last_task_date = date(2025, 1, 1)
        db_session.commit()

        midnight_jan2 = datetime(2025, 1, 2, 0, 0, tzinfo=timezone.utc)
        count = reset_expired_streaks(db_session, reference_date=midnight_jan2)
        assert count == 0

    def test_resets_null_last_task_date(self, db_session, seeded_db):
        """User with no last_task_date but current_streak > 0 gets reset."""
        orphan = models.User(
            nickname="Orphan", login_pin="9999", role_id=1,
            current_streak=2, last_task_date=None,
        )
        db_session.add(orphan)
        db_session.commit()

        midnight = datetime(2025, 1, 2, 0, 0, tzinfo=timezone.utc)
        count = reset_expired_streaks(db_session, reference_date=midnight)

        assert count == 1
        db_session.refresh(orphan)
        assert orphan.current_streak == 0
