
from backend import models
from tests.people import add_person


def test_get_roles(client, seeded_db):
    resp = client.get("/roles/")
    assert resp.status_code == 200, resp.text
    roles = resp.json()
    assert len(roles) >= 4  # Admin, Contributor, Teenager, Child


def test_create_role_api(client, db_session, seeded_db):
    resp = client.post(
        "/roles/", json={"name": "NewRole", "multiplier_value": 2.0})
    assert resp.status_code == 200, resp.text
    assert resp.json()["name"] == "NewRole"

    # Duplicate
    resp = client.post(
        "/roles/", json={"name": "NewRole", "multiplier_value": 2.0})
    assert resp.status_code == 400, resp.text


def test_update_role_api(client, db_session, seeded_db):
    # Create role
    resp = client.post(
        "/roles/", json={"name": "UpdateRole", "multiplier_value": 1.0})
    role_id = resp.json()["id"]

    # Update
    resp = client.put(f"/roles/{role_id}", json={"multiplier_value": 3.0})
    assert resp.status_code == 200, resp.text
    assert resp.json()["multiplier_value"] == 3.0

    # Invalid multiplier
    resp = client.put(f"/roles/{role_id}", json={"multiplier_value": -1.0})
    assert resp.status_code == 400, resp.text


def test_delete_role_api(client, db_session, seeded_db):
    # Create empty role
    resp = client.post(
        "/roles/", json={"name": "EmptyRole", "multiplier_value": 1.0})
    role_id = resp.json()["id"]

    # Delete
    resp = client.delete(f"/roles/{role_id}")
    assert resp.status_code == 200, resp.text

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
    add_person(db_session, "R1User", r1["id"])

    # Delete Role 1 without params -> Fail
    resp = client.delete(f"/roles/{r1['id']}")
    assert resp.status_code == 400, resp.text

    # Delete Role 1 with reassign -> Success
    resp = client.delete(f"/roles/{r1['id']}?reassign_to_role_id={r2['id']}")
    assert resp.status_code == 200, resp.text

    # Verify User is now in Role 2
    db_session.expire_all()
    user = db_session.query(models.User).filter(models.User.nickname == "R1User").one()
    assert user.role_id == r2["id"]
