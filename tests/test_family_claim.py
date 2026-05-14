import datetime
import pytest

from backend import crud, schemas, models
from backend.services import tasks as tasks_service
from backend.exceptions import AuthorizationError


def _make_role(db, name, multiplier):
    role = models.Role(name=name, multiplier_value=multiplier)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def _make_user(db, nickname, role_id):
    return crud.create_user(
        db,
        schemas.UserCreate(nickname=nickname, login_pin="0000", role_id=role_id),
    )


def _make_instance(db, task_id, user_id):
    instance = models.TaskInstance(
        task_id=task_id,
        user_id=user_id,
        due_time=datetime.datetime.now(),
        status="PENDING",
    )
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


def test_user_can_complete_own_task(db_session):
    import uuid

    uid = str(uuid.uuid4())[:8]
    role = _make_role(db_session, f"Parent_{uid}", 1.0)
    user = _make_user(db_session, f"Dad_{uid}", role.id)

    task = crud.create_task(
        db_session,
        schemas.TaskCreate(
            name=f"Dishes_{uid}",
            description="Wash up",
            base_points=10,
            assigned_role_id=role.id,
            schedule_type="daily",
            default_due_time="12:00",
        ),
    )

    instance = _make_instance(db_session, task.id, user.id)

    result = tasks_service.complete_task_instance(
        db_session, instance_id=instance.id, actual_user_id=user.id
    )

    assert result.status == "COMPLETED"
    assert result.user_id == user.id

    tx = db_session.query(models.Transaction).filter(
        models.Transaction.reference_instance_id == instance.id
    ).first()
    assert tx is not None
    assert tx.user_id == user.id
    assert tx.awarded_points == 15  # 10 base + 5 daily first-task bonus


def test_user_cannot_complete_another_users_task(db_session):
    import uuid

    uid = str(uuid.uuid4())[:8]
    role_p = _make_role(db_session, f"Parent2_{uid}", 1.0)
    role_t = _make_role(db_session, f"Teen2_{uid}", 1.5)

    user_p = _make_user(db_session, f"Dad2_{uid}", role_p.id)
    user_t = _make_user(db_session, f"Son2_{uid}", role_t.id)

    task = crud.create_task(
        db_session,
        schemas.TaskCreate(
            name=f"HeavyLifting_{uid}",
            description="Lift things",
            base_points=10,
            assigned_role_id=role_p.id,
            schedule_type="daily",
            default_due_time="12:00",
        ),
    )

    # Instance assigned to parent
    instance = _make_instance(db_session, task.id, user_p.id)

    with pytest.raises(AuthorizationError):
        tasks_service.complete_task_instance(
            db_session, instance_id=instance.id, actual_user_id=user_t.id
        )
