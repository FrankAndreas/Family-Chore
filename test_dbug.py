import pytest
from backend import crud, schemas, models
from backend.database import SessionLocal
import datetime

def test_debug(db_session, admin_user):
    crud.update_user(db_session, admin_user.id, schemas.UserUpdate(email="admin@example.com", notifications_enabled=True))
    task = crud.create_task(db_session, schemas.TaskCreate(
        name="Daily Task", description="Daily", base_points=10, assigned_role_id=admin_user.role_id,
        schedule_type="daily", default_due_time="12:00"
    ))
    instance = models.TaskInstance(
        task_id=task.id, user_id=admin_user.id, due_time=datetime.datetime.now(), status="PENDING"
    )
    db_session.add(instance)
    db_session.commit()
    start_of_day = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    q1 = db_session.query(models.User).filter(models.User.notifications_enabled == 1).count()
    q2 = db_session.query(models.User).filter(models.User.email.isnot(None)).count()
    q3 = db_session.query(models.TaskInstance).filter(models.TaskInstance.status == "PENDING").count()
    q4 = db_session.query(models.TaskInstance).filter(models.TaskInstance.due_time >= start_of_day).count()
    q5 = db_session.query(models.Task).filter(models.Task.schedule_type == "daily").count()
    
    # Try the join
    u = db_session.query(models.User).join(models.TaskInstance).all()
    print("q1:", q1, "q2:", q2, "q3:", q3, "q4:", q4, "q5:", q5, "joined_len:", len(u))
    assert False
