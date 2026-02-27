from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend import models


def test_login_auto_migrates_plaintext_pin(
    client: TestClient, db_session: Session, seeded_db: Session
):
    # 1. Create a user with a legacy plaintext PIN directly in the DB
    role = db_session.query(models.Role).first()
    user = models.User(
        nickname="LegacyUser",
        login_pin="1234",  # Plaintext!
        role_id=role.id,
        current_points=0,
        lifetime_points=0
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.login_pin == "1234"
    assert not user.login_pin.startswith("$2b$")

    # 2. Login with the correct PIN
    response = client.post("/login/", json={
        "nickname": "LegacyUser",
        "login_pin": "1234"
    })

    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data

    # 3. Verify the PIN was upgraded in the database
    db_session.refresh(user)
    assert user.login_pin != "1234"
    assert (user.login_pin.startswith("$2b$") or
            user.login_pin.startswith("$2a$"))

    # 4. Verify we can login AGAIN with the newly hashed PIN
    response2 = client.post("/login/", json={
        "nickname": "LegacyUser",
        "login_pin": "1234"
    })
    assert response2.status_code == 200, response2.text


def test_login_rejects_incorrect_plaintext_pin(
    client: TestClient, db_session: Session, seeded_db: Session
):
    role = db_session.query(models.Role).first()
    user = models.User(
        nickname="WrongPinUser",
        login_pin="1234",  # Plaintext
        role_id=role.id,
        current_points=0,
        lifetime_points=0
    )
    db_session.add(user)
    db_session.commit()

    # Login with WRONG PIN
    response = client.post("/login/", json={
        "nickname": "WrongPinUser",
        "login_pin": "9999"
    })

    assert response.status_code == 401, response.text

    # Verify it was NOT upgraded
    db_session.refresh(user)
    assert user.login_pin == "1234"
