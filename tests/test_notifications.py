from backend import crud, schemas
from backend.notifications_service import send_email_background
from fastapi import BackgroundTasks


def test_create_notification(db_session, admin_user):
    # Create a notification via CRUD
    notif = crud.create_notification(
        db_session,
        schemas.NotificationCreate(
            user_id=admin_user.id,
            type="SYSTEM",
            title="Test Notification",
            message="This is a test."
        )
    )
    assert notif.id is not None
    assert notif.user_id == admin_user.id
    assert notif.read is False or notif.read == 0


def test_get_notifications_api(client, admin_user, db_session):
    # Create a notification first
    crud.create_notification(
        db_session,
        schemas.NotificationCreate(
            user_id=admin_user.id,
            type="SYSTEM",
            title="Test API",
            message="Message"
        )
    )

    # Fetch via API
    response = client.get(f"/notifications/{admin_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["title"] == "Test API"


def test_mark_read_api(client, admin_user, db_session):
    # Create notification
    notif = crud.create_notification(
        db_session,
        schemas.NotificationCreate(
            user_id=admin_user.id,
            type="SYSTEM",
            title="Read Me",
            message="Message"
        )
    )

    # Mark as read
    response = client.post(
        f"/notifications/{notif.id}/read?user_id={admin_user.id}")
    assert response.status_code == 200
    assert response.json()["read"] == 1

    # Verify in DB
    db_session.refresh(notif)
    assert notif.read == 1


def test_mark_all_read_api(client, admin_user, db_session):
    # Create two notifications
    crud.create_notification(
        db_session,
        schemas.NotificationCreate(
            user_id=admin_user.id,
            type="SYS",
            title="1",
            message="1"
        )
    )
    crud.create_notification(
        db_session,
        schemas.NotificationCreate(
            user_id=admin_user.id,
            type="SYS",
            title="2",
            message="2"
        )
    )

    # Mark all read
    response = client.post(f"/notifications/read-all?user_id={admin_user.id}")
    assert response.status_code == 200
    assert response.json() is True

    # Verify
    unreads = crud.get_user_notifications(
        db_session, admin_user.id, unread_only=True)
    assert len(unreads) == 0


def test_get_notifiable_admins(db_session, admin_user):
    # Admin starts without email
    assert admin_user.email is None
    admins = crud.get_notifiable_admins(db_session)
    assert len(admins) == 0

    # Add email and enable notifications
    crud.update_user(db_session, admin_user.id, schemas.UserUpdate(
        email="admin@example.com", notifications_enabled=True))
    admins = crud.get_notifiable_admins(db_session)
    assert len(admins) == 1
    assert admins[0].email == "admin@example.com"


def test_send_email_background():
    # Test the BackgroundTasks wrapper queues the function correctly
    bg_tasks = BackgroundTasks()
    send_email_background(bg_tasks, "test@example.com", "Subject", "Body")

    assert len(bg_tasks.tasks) == 1
    task_queued = bg_tasks.tasks[0]
    assert task_queued.func.__name__ == "send_email_sync"
    assert task_queued.args == ("test@example.com", "Subject", "Body")
