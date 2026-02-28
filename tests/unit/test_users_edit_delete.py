
from fastapi.testclient import TestClient
from backend import models, security


def setup_normal_user(db_session):
    user_role = db_session.query(models.Role).filter(models.Role.name == "Contributor").first()
    normal_user = models.User(
        nickname="NormalUser",
        login_pin=security.get_password_hash("1234"),
        role_id=user_role.id
    )
    db_session.add(normal_user)
    db_session.commit()
    db_session.refresh(normal_user)
    return normal_user


def test_update_user_profile(client: TestClient, db_session):
    normal_user = setup_normal_user(db_session)
    user_role = db_session.query(models.Role).filter(models.Role.name == "Contributor").first()

    # Admin updates normal user
    res = client.put(f"/users/{normal_user.id}", json={
        "nickname": "UpdatedNick",
        "role_id": user_role.id
    })
    assert res.status_code == 200
    assert res.json()["nickname"] == "UpdatedNick"


def test_reset_user_password(client: TestClient, db_session):
    normal_user = setup_normal_user(db_session)
    # Admin resets normal user password
    res = client.put(f"/users/{normal_user.id}/password", json={
        "new_pin": "5555"
    })
    assert res.status_code == 200
    assert res.json()["success"] is True


def test_delete_user(client: TestClient, db_session):
    normal_user = setup_normal_user(db_session)

    # Admin deletes normal user
    res = client.delete(f"/users/{normal_user.id}")
    assert res.status_code == 200
    assert res.json()["success"] is True

    # Verify user is gone
    get_res = client.get("/users/")
    assert normal_user.id not in [u["id"] for u in get_res.json()]


def test_delete_self_fails(client: TestClient, db_session, admin_user):
    res = client.delete(f"/users/{admin_user.id}")
    assert res.status_code == 400
    assert "Cannot delete yourself" in res.json()["detail"]
