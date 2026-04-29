import pytest
from datetime import datetime, timezone
from backend.services.gamification import award_points_for_task, reset_expired_streaks
from backend import models


def _awarded_points(db, instance_id: int) -> int:
    """Look up awarded_points from the Transaction linked to a TaskInstance."""
    txn = db.query(models.Transaction).filter(
        models.Transaction.reference_instance_id == instance_id
    ).first()
    return txn.awarded_points if txn else 0


@pytest.fixture
def setup_test_users(db_session, seeded_db):
    parent = models.User(nickname="Parent", login_pin="1111", role_id=1)
    teen = models.User(nickname="Teen", login_pin="2222", role_id=3)
    child = models.User(nickname="Child", login_pin="3333", role_id=4)
    db_session.add_all([parent, teen, child])
    db_session.commit()
    return {"parent": parent, "teen": teen, "child": child}


def test_streak_first_task(db_session, setup_test_users):
    """Completing the first task should start a streak and award daily bonus"""
    child = setup_test_users["child"]
    task = models.Task(name="Streak 1", description="yes", default_due_time="12:00",
                       base_points=100, schedule_type="daily")
    db_session.add(task)
    db_session.commit()

    instance = models.TaskInstance(task_id=task.id, user_id=child.id, status="PENDING",
                                   due_time=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc))
    db_session.add(instance)
    db_session.commit()

    now = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)

    # Pre-condition
    assert child.current_streak == 0
    assert child.last_task_date is None

    # Execute
    award_points_for_task(db_session, instance, current_time=now)

    # Assert
    assert child.current_streak == 1
    assert child.last_task_date == now.date()
    # base * mult + daily_bonus: 100 * 1.5 (role) + 5 = 155
    assert _awarded_points(db_session, instance.id) == 155


def test_streak_same_day(db_session, setup_test_users):
    """Completing a second task on the same day shouldn't increase streak or award daily bonus"""
    child = setup_test_users["child"]
    task1 = models.Task(name="T1", description="yes", default_due_time="12:00",
                        base_points=100, schedule_type="daily")
    task2 = models.Task(name="T2", description="yes", default_due_time="12:00",
                        base_points=100, schedule_type="daily")
    db_session.add_all([task1, task2])
    db_session.commit()

    inst1 = models.TaskInstance(task_id=task1.id, user_id=child.id, status="PENDING",
                                due_time=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc))
    inst2 = models.TaskInstance(task_id=task2.id, user_id=child.id, status="PENDING",
                                due_time=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc))
    db_session.add_all([inst1, inst2])
    db_session.commit()

    now1 = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
    now2 = datetime(2025, 1, 1, 14, 0, tzinfo=timezone.utc)

    award_points_for_task(db_session, inst1, current_time=now1)

    # Should be streak 1
    assert child.current_streak == 1
    assert _awarded_points(db_session, inst1.id) == 155

    award_points_for_task(db_session, inst2, current_time=now2)

    # Should STILL be streak 1, no daily bonus
    assert child.current_streak == 1
    assert _awarded_points(db_session, inst2.id) == 150


def test_streak_consecutive_days(db_session, setup_test_users):
    """Completing tasks on consecutive days should increment streak and multiplier up to 0.5"""
    child = setup_test_users["child"]

    for day in range(1, 8):
        task = models.Task(name=f"T{day}", description="yes", default_due_time="12:00",
                           base_points=100, schedule_type="daily")
        db_session.add(task)
        db_session.commit()
        inst = models.TaskInstance(task_id=task.id, user_id=child.id, status="PENDING",
                                   due_time=datetime(2025, 1, day, 12, 0, tzinfo=timezone.utc))
        db_session.add(inst)
        db_session.commit()

        now = datetime(2025, 1, day, 12, 0, tzinfo=timezone.utc)
        award_points_for_task(db_session, inst, current_time=now)

        # Determine expected multiplier (+0.1 per streak day past 1, max +0.5)
        # Day 1: +0  (Total 1.0) -> Pts: 105
        # Day 2: +0.1 (Total 1.1) -> Pts: 115
        # Day 3: +0.2 (Total 1.2) -> Pts: 125
        # Day 6: +0.5 (Total 1.5) -> Pts: 155
        # Day 7: +0.5 (Total 1.5) -> Pts: 155
        assert child.current_streak == day

        expected_bonus = min(0.5, (day - 1) * 0.1)
        expected_points = int(100 * (1.5 + expected_bonus)) + 5
        assert _awarded_points(db_session, inst.id) == expected_points


def test_streak_missed_day(db_session, setup_test_users):
    """Missing a day should reset streak to 1"""
    child = setup_test_users["child"]

    task1 = models.Task(name="T1", description="yes", default_due_time="12:00",
                        base_points=100, schedule_type="daily")
    task2 = models.Task(name="T2", description="yes", default_due_time="12:00",
                        base_points=100, schedule_type="daily")
    db_session.add_all([task1, task2])
    db_session.commit()

    inst1 = models.TaskInstance(task_id=task1.id, user_id=child.id, status="PENDING",
                                due_time=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc))
    inst2 = models.TaskInstance(task_id=task2.id, user_id=child.id, status="PENDING",
                                due_time=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc))
    db_session.add_all([inst1, inst2])
    db_session.commit()

    # Day 1
    now1 = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
    award_points_for_task(db_session, inst1, current_time=now1)
    assert child.current_streak == 1

    # Day 3 (Missed day 2)
    now3 = datetime(2025, 1, 3, 12, 0, tzinfo=timezone.utc)
    award_points_for_task(db_session, inst2, current_time=now3)

    assert child.current_streak == 1
    assert _awarded_points(db_session, inst2.id) == 155  # Streak broke, so back to base + daily_bonus


def test_reset_expired_streaks(db_session, setup_test_users):
    """cronjob function should zero out expired streaks"""
    child = setup_test_users["child"]
    teen = setup_test_users["teen"]

    # Child played yesterday. Streak holds.
    child.last_task_date = datetime(2025, 1, 1, tzinfo=timezone.utc).date()
    child.current_streak = 5

    # Teen played 2 days ago. Streak expires.
    teen.last_task_date = datetime(2025, 1, 1, tzinfo=timezone.utc).date()
    teen.current_streak = 5

    db_session.commit()

    # Run midnight reset for Jan 3 (Child played Jan 1, so Child expires too! Wait.
    # Let's say today is Jan 2. Child played Jan 1 (yesterday). Teen played Dec 31 (2 days ago).
    teen.last_task_date = datetime(2024, 12, 31, tzinfo=timezone.utc).date()
    db_session.commit()

    midnight_jan2 = datetime(2025, 1, 2, 0, 0, tzinfo=timezone.utc)
    resets = reset_expired_streaks(db_session, reference_date=midnight_jan2)

    assert resets == 1

    db_session.refresh(child)
    db_session.refresh(teen)

    assert child.current_streak == 5  # Safe (was yesterday)
    assert teen.current_streak == 0  # Reset (2 days ago)
