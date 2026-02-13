
import pytest
from datetime import datetime, timedelta
from backend import crud, models


@pytest.fixture
def scheduler_setup(db_session, seeded_db):
    # Users
    role = db_session.query(models.Role).filter(models.Role.name == "Contributor").first()
    u1 = models.User(nickname="U1", login_pin="0000", role_id=role.id)
    u2 = models.User(nickname="U2", login_pin="0000", role_id=role.id)
    db_session.add_all([u1, u2])
    db_session.commit()

    return {"u1": u1, "u2": u2, "role": role}


def test_generate_daily_instances_daily_task(db_session, scheduler_setup):
    # Daily task
    task = models.Task(
        name="Daily", description="D", base_points=10,
        schedule_type="daily", default_due_time="10:00",
        assigned_role_id=scheduler_setup["role"].id
    )
    db_session.add(task)
    db_session.commit()

    # Run generation
    count = crud.generate_daily_instances(db_session)

    # Should create 2 instances (one for each user in role)
    assert count == 2

    # Run again -> should be 0 (idempotency)
    count = crud.generate_daily_instances(db_session)
    assert count == 0


def test_generate_daily_instances_weekly_skip(db_session, scheduler_setup):
    # Weekly task for TOMORROW (or just not today)
    today_weekday = datetime.now().strftime("%A")
    wrong_day = "Tuesday" if today_weekday != "Tuesday" else "Wednesday"

    task = models.Task(
        name="WeeklyWrong", description="W", base_points=10,
        schedule_type="weekly", default_due_time=wrong_day
    )
    db_session.add(task)
    db_session.commit()

    count = crud.generate_daily_instances(db_session)
    assert count == 0


def test_generate_daily_instances_weekly_hit(db_session, scheduler_setup):
    # Weekly task for TODAY
    today_weekday = datetime.now().strftime("%A")

    task = models.Task(
        name="WeeklyRight", description="W", base_points=10,
        schedule_type="weekly", default_due_time=today_weekday
    )
    db_session.add(task)
    db_session.commit()

    count = crud.generate_daily_instances(db_session)
    # Should generate for ALL users since no role assigned
    # We have 2 users created in fixture + Admin created by seeded_db + default roles?
    # seeded_db creates roles, admin_user fixture creates TestAdmin.
    # scheduler_setup creates U1, U2.
    # So total users = 2.

    assert count == 2


def test_generate_daily_instances_recurring(db_session, scheduler_setup):
    # Recurring with cooldown
    task = models.Task(
        name="Recurring", description="R", base_points=10,
        schedule_type="recurring", default_due_time="X", recurrence_min_days=2
    )
    db_session.add(task)
    db_session.commit()

    # 1. First run -> 2 instances (U1, U2)
    count = crud.generate_daily_instances(db_session)
    assert count == 2

    # 2. Complete U1's instance TODAY
    instance = db_session.query(models.TaskInstance).filter(
        models.TaskInstance.task_id == task.id,
        models.TaskInstance.user_id == scheduler_setup["u1"].id
    ).first()
    instance.status = "COMPLETED"
    instance.completed_at = datetime.now()
    db_session.commit()

    # 3. Time travel to Tomorrow
    # We mock check that checks DATE diffs.
    # If completed TODAY, diff is 0 days. 0 < 2 -> Skip.

    count = crud.generate_daily_instances(db_session)
    assert count == 0

    # 4. Modify completion date to 3 days ago
    instance.completed_at = datetime.now() - timedelta(days=3)
    db_session.commit()

    # Note: `generate_daily_instances` also checks for EXISTING pending instances for today.
    # U2 still has a PENDING instance from step 1.
    # So `generate_daily_instances` will see U2 has an instance and skip U2.

    count = crud.generate_daily_instances(db_session)
    assert count == 1  # Only U1 gets a new one
