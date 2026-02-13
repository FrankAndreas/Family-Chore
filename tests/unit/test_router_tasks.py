

from datetime import datetime
from backend import models


def test_create_task_api(client, db_session, seeded_db):
    role = db_session.query(models.Role).filter(models.Role.name == "Contributor").first()

    resp = client.post("/tasks/", json={
        "name": "APITask",
        "description": "Desc",
        "base_points": 100,
        "assigned_role_id": role.id,
        "schedule_type": "daily",
        "default_due_time": "12:00"
    })
    assert resp.status_code == 200
    assert resp.json()["name"] == "APITask"


def test_get_tasks_api(client, db_session, seeded_db):
    resp = client.get("/tasks/")
    assert resp.status_code == 200


def test_update_task_api(client, db_session, seeded_db):
    # Create
    role = db_session.query(models.Role).first()
    resp_create = client.post("/tasks/", json={
        "name": "ToUpdate", "description": "Desc", "base_points": 10, "assigned_role_id": role.id,
        "schedule_type": "daily", "default_due_time": "10:00"
    })
    assert resp_create.status_code == 200, f"Create failed: {resp_create.text}"
    t = resp_create.json()

    # Update
    resp = client.put(f"/tasks/{t['id']}", json={"name": "UpdatedName", "description": "Desc"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "UpdatedName"

    # Update non-existent
    resp = client.put("/tasks/9999", json={"name": "Ghost"})
    assert resp.status_code == 404


def test_delete_task_api(client, db_session, seeded_db):
    # Create
    role = db_session.query(models.Role).first()
    resp_create = client.post("/tasks/", json={
        "name": "ToDelete", "description": "Desc", "base_points": 10, "assigned_role_id": role.id,
        "schedule_type": "daily", "default_due_time": "10:00"
    })
    assert resp_create.status_code == 200, f"Create failed: {resp_create.text}"
    t = resp_create.json()

    # Delete
    resp = client.delete(f"/tasks/{t['id']}")
    assert resp.status_code == 200

    # Verify gone
    resp = client.get("/tasks/")
    ids = [x["id"] for x in resp.json()]
    assert t['id'] not in ids

    # Delete non-existent
    resp = client.delete("/tasks/9999")
    assert resp.status_code == 404


def test_export_tasks_api(client, db_session, seeded_db):
    resp = client.get("/tasks/export")
    assert resp.status_code == 200
    data = resp.json()
    assert "tasks" in data
    assert data["version"] == "1.0"


def test_import_tasks_api(client, db_session, seeded_db):
    payload = {
        "tasks": [
            {
                "name": "ImportedTask",
                "description": "Desc",
                "base_points": 50,
                "assigned_role": "Contributor",  # Role name lookup
                "schedule_type": "daily",
                "default_due_time": "09:00"
            }
        ],
        "skip_duplicates": True
    }
    resp = client.post("/tasks/import", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "ImportedTask" in data["created"]

    # Test duplicate skip
    resp = client.post("/tasks/import", json=payload)
    assert resp.status_code == 200
    assert "ImportedTask" in resp.json()["skipped"]


def test_complete_task_instance_api(client, db_session, seeded_db):
    # Setup: User, Task, Instance
    role = db_session.query(models.Role).first()

    # Create Task
    task = models.Task(name="InstTask", description="D", base_points=10,
                       assigned_role_id=role.id, schedule_type="daily", default_due_time="12:00")
    db_session.add(task)
    db_session.commit()

    # Create User
    user = models.User(nickname="InstUser", login_pin="1111", role_id=role.id)
    db_session.add(user)
    db_session.commit()

    # Create Instance
    instance = models.TaskInstance(task_id=task.id, user_id=user.id, due_time=datetime.now(), status="PENDING")
    db_session.add(instance)
    db_session.commit()

    # Complete
    resp = client.post(f"/tasks/{instance.id}/complete")
    assert resp.status_code == 200
    assert resp.json()["status"] == "COMPLETED"

    # Verify points
    db_session.refresh(user)
    # 10 * multiplier (likely 1.0 or whatever role has)
    assert user.current_points > 0

    # Complete non-existent
    resp = client.post("/tasks/9999/complete")
    assert resp.status_code == 404


def test_get_user_daily_tasks(client, db_session, seeded_db):
    # We need a user ID from seeded_db or create one
    users = client.get("/users/").json()
    if not users:
        # Create one
        role = db_session.query(models.Role).first()
        u = client.post("/users/", json={"nickname": "DailyUser", "login_pin": "0000", "role_id": role.id}).json()
        uid = u["id"]
    else:
        uid = users[0]["id"]

    resp = client.get(f"/tasks/daily/{uid}")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_pending_tasks(client, db_session, seeded_db):
    resp = client.get("/tasks/pending")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
