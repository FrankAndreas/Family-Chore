
from backend import models


def test_create_user_api(client, db_session, seeded_db):
    # Role is needed
    role = db_session.query(models.Role).filter(
        models.Role.name == "Contributor").first()

    response = client.post("/users/", json={
        "nickname": "APIUser",
        "login_pin": "5678",
        "role_id": role.id
    })
    assert response.status_code == 200
    data = response.json()
    assert data["nickname"] == "APIUser"
    assert "id" in data


def test_create_user_duplicate_nickname(client, db_session, seeded_db):
    # Admin exists
    role = db_session.query(models.Role).filter(
        models.Role.name == "Contributor").first()

    # Create the user first to ensure it exists for duplicate check
    client.post("/users/", json={
        "nickname": "Admin",
        "login_pin": "1234",
        "role_id": role.id
    })

    response = client.post("/users/", json={
        "nickname": "Admin",  # Already exists
        "login_pin": "1234",
        "role_id": role.id
    })
    assert response.status_code == 400
    assert "Nickname already registered" in response.json()["detail"]


def test_login_success(client, seeded_db):
    # Login as Admin (pin 1234 from seeded_db generic flow, or we create one?)
    pass


def test_login_flow(client, db_session, seeded_db):
    role = db_session.query(models.Role).first()
    client.post("/users/", json={"nickname": "LoginUser",
                "login_pin": "9999", "role_id": role.id})

    # Correct login
    resp = client.post(
        "/login/", json={"nickname": "LoginUser", "login_pin": "9999"})
    assert resp.status_code == 200
    assert resp.json()["nickname"] == "LoginUser"

    # Wrong PIN
    resp = client.post(
        "/login/", json={"nickname": "LoginUser", "login_pin": "0000"})
    assert resp.status_code == 401

    # Wrong User
    resp = client.post(
        "/login/", json={"nickname": "Ghost", "login_pin": "9999"})
    assert resp.status_code == 404


def test_get_roles(client, seeded_db):
    resp = client.get("/roles/")
    assert resp.status_code == 200
    roles = resp.json()
    assert len(roles) >= 4  # Admin, Contributor, Teenager, Child


def test_create_role_api(client, db_session, seeded_db):
    resp = client.post(
        "/roles/", json={"name": "NewRole", "multiplier_value": 2.0})
    assert resp.status_code == 200
    assert resp.json()["name"] == "NewRole"

    # Duplicate
    resp = client.post(
        "/roles/", json={"name": "NewRole", "multiplier_value": 2.0})
    assert resp.status_code == 400


def test_update_role_api(client, db_session, seeded_db):
    # Create role
    resp = client.post(
        "/roles/", json={"name": "UpdateRole", "multiplier_value": 1.0})
    role_id = resp.json()["id"]

    # Update
    resp = client.put(f"/roles/{role_id}", json={"multiplier_value": 3.0})
    assert resp.status_code == 200
    assert resp.json()["multiplier_value"] == 3.0

    # Invalid multiplier
    resp = client.put(f"/roles/{role_id}", json={"multiplier_value": -1.0})
    assert resp.status_code == 400


def test_delete_role_api(client, db_session, seeded_db):
    # Create empty role
    resp = client.post(
        "/roles/", json={"name": "EmptyRole", "multiplier_value": 1.0})
    role_id = resp.json()["id"]

    # Delete
    resp = client.delete(f"/roles/{role_id}")
    assert resp.status_code == 200

    # Verify gone
    resp = client.get("/roles/")
    ids = [r["id"] for r in resp.json()]
    assert role_id not in ids


def test_delete_role_with_users_reassign(client, db_session, seeded_db):
    # Role 1
    r1 = client.post(
        "/roles/", json={"name": "Role1", "multiplier_value": 1.0}).json()
    # Role 2
    r2 = client.post(
        "/roles/", json={"name": "Role2", "multiplier_value": 1.0}).json()

    # User in Role 1
    client.post("/users/", json={"nickname": "R1User",
                "login_pin": "1234", "role_id": r1["id"]})

    # Delete Role 1 without params -> Fail
    resp = client.delete(f"/roles/{r1['id']}")
    assert resp.status_code == 400

    # Delete Role 1 with reassign -> Success
    resp = client.delete(f"/roles/{r1['id']}?reassign_to_role_id={r2['id']}")
    assert resp.status_code == 200

    # Verify User is now in Role 2
    # We don't have get_user endpoints that show role_id easily?
    # Login again to check role_id
    login_resp = client.post(
        "/login/", json={"nickname": "R1User", "login_pin": "1234"})
    assert login_resp.json()["role_id"] == r2["id"]
