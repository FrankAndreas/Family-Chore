
from backend import models


def test_create_reward_api(client, db_session, seeded_db):
    resp = client.post("/rewards/", json={
        "name": "APIReward",
        "description": "Desc",
        "cost_points": 50,
        "tier_level": 1
    })
    assert resp.status_code == 200
    assert resp.json()["name"] == "APIReward"
    assert resp.json()["cost_points"] == 50


def test_get_rewards_api(client, db_session, seeded_db):
    resp = client.get("/rewards/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_set_user_goal_api(client, db_session, seeded_db):
    # Setup
    role = db_session.query(models.Role).first()
    user = client.post(
        "/users/", json={"nickname": "GoalUser", "login_pin": "1234", "role_id": role.id}).json()
    reward = client.post(
        "/rewards/", json={"name": "GoalReward", "cost_points": 100}).json()

    # Set Goal
    resp = client.post(f"/users/{user['id']}/goal?reward_id={reward['id']}")
    assert resp.status_code == 200

    # Verify (Need to fetch user again? Response returns User)
    assert resp.json()["current_goal_reward_id"] == reward['id']


def test_redeem_reward_api_insufficient_points(client, db_session, seeded_db):
    # Setup
    role = db_session.query(models.Role).first()
    user = client.post(
        "/users/", json={"nickname": "PoorUser", "login_pin": "1234", "role_id": role.id}).json()
    reward = client.post(
        "/rewards/", json={"name": "Expensive", "cost_points": 1000}).json()

    # Redeem
    resp = client.post(f"/rewards/{reward['id']}/redeem?user_id={user['id']}")
    assert resp.status_code == 400
    assert "Insufficient points" in resp.json()["detail"]


def test_redeem_reward_api_success(client, db_session, seeded_db):
    # Setup
    role = db_session.query(models.Role).first()
    # Need user with points. Can't set points directly via API easily (unless we complete tasks).
    # Let's use direct DB manipulation for setup speed.
    user_db = models.User(nickname="RichUser", login_pin="1234",
                          role_id=role.id, current_points=100)
    db_session.add(user_db)
    db_session.commit()

    reward = client.post(
        "/rewards/", json={"name": "Cheap", "cost_points": 50}).json()

    # Redeem
    resp = client.post(f"/rewards/{reward['id']}/redeem?user_id={user_db.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["remaining_points"] == 50


def test_redeem_split_api(client, db_session, seeded_db):
    # Setup generic users
    role = db_session.query(models.Role).first()
    u1 = models.User(nickname="U1", login_pin="1",
                     role_id=role.id, current_points=50)
    u2 = models.User(nickname="U2", login_pin="1",
                     role_id=role.id, current_points=50)
    db_session.add_all([u1, u2])
    db_session.commit()

    reward = client.post(
        "/rewards/", json={"name": "Splittable", "cost_points": 100}).json()

    payload = {
        "contributions": [
            {"user_id": u1.id, "points": 50},
            {"user_id": u2.id, "points": 50}
        ]
    }

    resp = client.post(f"/rewards/{reward['id']}/redeem-split", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["total_points"] == 100
