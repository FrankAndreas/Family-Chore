
import pytest
from datetime import datetime, timedelta
from backend import crud, models, schemas


@pytest.fixture
def task_setup(db_session, seeded_db):
    # Create a user
    role = db_session.query(models.Role).filter(
        models.Role.name == "Contributor").first()
    user = models.User(nickname="TaskUser", login_pin="1234", role_id=role.id)
    db_session.add(user)
    db_session.commit()

    # Create a task
    task = models.Task(
        name="Test Task",
        description="Do something",
        base_points=100,
        schedule_type="daily",
        default_due_time="17:00",
        assigned_role_id=role.id
    )
    db_session.add(task)
    db_session.commit()

    return {"user": user, "task": task, "role": role}


def test_update_task(db_session, task_setup):
    task = task_setup["task"]

    update_data = schemas.TaskUpdate(
        name="Updated Task",
        base_points=150
    )

    updated = crud.update_task(db_session, task.id, update_data)

    assert updated.name == "Updated Task"
    assert updated.base_points == 150
    assert updated.description == "Do something"  # Unchanged

    # Verify persistence
    db_session.refresh(task)
    assert task.name == "Updated Task"


def test_update_task_not_found(db_session):
    update_data = schemas.TaskUpdate(name="Ghost")
    assert crud.update_task(db_session, 9999, update_data) is None


def test_delete_task(db_session, task_setup):
    task = task_setup["task"]
    user = task_setup["user"]

    # Create an instance to verify cascade delete
    instance = models.TaskInstance(
        task_id=task.id,
        user_id=user.id,
        due_time=datetime.now(),
        status="PENDING"
    )
    db_session.add(instance)
    db_session.commit()
    db_session.refresh(instance)
    instance_id = instance.id

    # Delete task
    result = crud.delete_task(db_session, task.id)
    assert result is True

    # Verify task is gone
    assert db_session.query(models.Task).filter(
        models.Task.id == task.id).first() is None

    # Verify instance is gone (cascade)
    assert db_session.query(models.TaskInstance).filter(
        models.TaskInstance.id == instance_id).first() is None


def test_delete_task_not_found(db_session):
    assert crud.delete_task(db_session, 9999) is False


def test_generate_instances_weekly_wrong_day(db_session, task_setup):
    # Create a weekly task for a day that is NOT today
    today_weekday = datetime.now().strftime("%A")
    wrong_day = "Tuesday" if today_weekday != "Tuesday" else "Wednesday"

    task_data = schemas.TaskCreate(
        name="Weekly Task",
        description="Once a week",
        base_points=200,
        schedule_type="weekly",
        default_due_time=wrong_day
    )
    task = crud.create_task(db_session, task_data)

    # verify creating the task triggered generation (which should return 0)
    # create_task calls generate_instances_for_task internally

    instances = db_session.query(models.TaskInstance).filter(
        models.TaskInstance.task_id == task.id).all()
    assert len(instances) == 0


def test_generate_instances_weekly_correct_day(db_session, task_setup):
    today_weekday = datetime.now().strftime("%A")

    task_data = schemas.TaskCreate(
        name="Weekly Task Today",
        description="Do it now",
        base_points=200,
        schedule_type="weekly",
        default_due_time=today_weekday,
        assigned_role_id=task_setup["role"].id
    )

    # This should generate an instance
    task = crud.create_task(db_session, task_data)

    instances = db_session.query(models.TaskInstance).filter(
        models.TaskInstance.task_id == task.id).all()
    assert len(instances) == 1
    assert instances[0].user_id == task_setup["user"].id


def test_generate_instances_recurring_cooldown(db_session, task_setup):
    role = task_setup["role"]

    # Recurring task with 3 days min cooldown
    task = models.Task(
        name="recurring", description="desc", base_points=10,
        schedule_type="recurring", default_due_time="ignored",
        recurrence_min_days=3, assigned_role_id=role.id
    )
    db_session.add(task)
    db_session.commit()

    # 1. First generation - should succeed (no history)
    count = crud.generate_instances_for_task(db_session, task)
    assert count == 1

    # Mark as completed YESTERDAY
    instance = db_session.query(models.TaskInstance).filter(
        models.TaskInstance.task_id == task.id
    ).first()
    instance.status = "COMPLETED"
    instance.completed_at = datetime.now() - timedelta(days=1)
    db_session.commit()

    # 2. Second generation - should fail (1 day < 3 days)
    count = crud.generate_instances_for_task(db_session, task)
    assert count == 0

    # Update completion to 4 days ago
    instance.completed_at = datetime.now() - timedelta(days=4)
    db_session.commit()

    # 3. Third generation - should succeed (4 days >= 3 days)
    # Note: generate_instances_for_task checks for EXISTING instances for today.
    # We hack the old instance's due_time to be in the past too, so it doesn't block new generation.
    instance.due_time = datetime.now() - timedelta(days=4)
    db_session.commit()

    count = crud.generate_instances_for_task(db_session, task)
    assert count == 1


def test_get_all_pending_tasks(db_session, task_setup):
    # Only pending tasks for today/future should be returned

    # Create a completed task
    crud.create_task(db_session, schemas.TaskCreate(
        name="Active Task", description="d", base_points=10, default_due_time="12:00"
    ))

    pending = crud.get_all_pending_tasks(db_session)
    # At least the one we just created (plus maybe setup ones)
    assert len(pending) >= 1

    # Mark one as completed
    t = pending[0]
    t.status = "COMPLETED"
    db_session.commit()

    pending_new = crud.get_all_pending_tasks(db_session)
    assert t.id not in [x.id for x in pending_new]
