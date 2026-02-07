import pytest
from backend import crud, schemas, models
from backend.database import SessionLocal, Base, engine

# Setup test DB
Base.metadata.create_all(bind=engine)


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_family_dashboard_claim_logic(db):
    import uuid
    import datetime
    unique_id = str(uuid.uuid4())[:8]

    # 1. Setup Data
    # Create Role 1 (Parent, x1.0)
    role_p = models.Role(name=f"FD_Parent_{unique_id}", multiplier_value=1.0)
    db.add(role_p)

    # Create Role 2 (Teen, x1.5)
    role_t = models.Role(name=f"FD_Teen_{unique_id}", multiplier_value=1.5)
    db.add(role_t)
    db.commit()
    db.refresh(role_p)
    db.refresh(role_t)

    # Create User A (Parent)
    user_p = crud.create_user(
        db,
        schemas.UserCreate(
            nickname=f"FD_Dad_{unique_id}", login_pin="0000", role_id=role_p.id
        )
    )
    # Create User B (Teen)
    user_t = crud.create_user(
        db,
        schemas.UserCreate(
            nickname=f"FD_Son_{unique_id}", login_pin="0000", role_id=role_t.id
        )
    )

    # Create Task (Assigned to Parent, 10 points)
    task = crud.create_task(db, schemas.TaskCreate(
        name=f"Heavy Lifting_{unique_id}",
        description="Lift things",
        base_points=10,
        assigned_role_id=role_p.id,
        schedule_type="daily",
        default_due_time="12:00"
    ))

    # Generate Instance
    # Force manual instance creation to avoid 'daily reset' complexity
    instance = models.TaskInstance(
        task_id=task.id,
        user_id=user_p.id,  # Assigned to Dad
        due_time=datetime.datetime.now(),
        status="PENDING"
    )
    db.add(instance)
    db.commit()
    db.refresh(instance)

    assert instance.user_id == user_p.id

    # 2. Test: Teenager Claims the task
    # Call complete_task_instance with actual_user_id = user_t.id
    completed_instance = crud.complete_task_instance(
        db, instance_id=instance.id, actual_user_id=user_t.id
    )

    # 3. Verify
    assert completed_instance is not None
    assert completed_instance.status == "COMPLETED"

    # Verify Reassignment
    assert completed_instance.user_id == user_t.id  # Should now be Son

    # Verify Transaction (Teen gets 1.5x points = 15)
    tx = db.query(models.Transaction).filter(
        models.Transaction.reference_instance_id == instance.id
    ).first()
    assert tx is not None
    assert tx.user_id == user_t.id
    assert tx.multiplier_used == 1.5
    assert tx.awarded_points == 15

    # Verify Original Task Definition Unchanged
    # The task definition should still be assigned to Role Parent
    original_task = db.query(models.Task).filter(
        models.Task.id == task.id
    ).first()
    assert original_task.assigned_role_id == role_p.id
