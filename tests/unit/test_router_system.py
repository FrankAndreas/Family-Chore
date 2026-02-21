
from backend import models


def test_get_default_language_api(client, db_session, seeded_db):
    resp = client.get("/settings/language/default")
    assert resp.status_code == 200
    data = resp.json()
    # seeded_db or default might set it to 'en'
    assert "value" in data
    assert "key" in data


def test_set_default_language_api(client, db_session, seeded_db):
    resp = client.put("/settings/language/default", json={
        "key": "default_language",
        "value": "de",
        "description": "German"
    })
    assert resp.status_code == 200
    assert resp.json()["value"] == "de"

    # Verify persistence
    resp = client.get("/settings/language/default")
    assert resp.json()["value"] == "de"


def test_update_user_language_api(client, db_session, seeded_db):
    # Setup user
    role = db_session.query(models.Role).first()
    u = models.User(nickname="LangUser", login_pin="1111", role_id=role.id)
    db_session.add(u)
    db_session.commit()

    # Update language
    resp = client.put(f"/users/{u.id}/language",
                      json={"preferred_language": "de"})
    assert resp.status_code == 200
    assert resp.json()["preferred_language"] == "de"

    # Update to null (default)
    resp = client.put(f"/users/{u.id}/language",
                      json={"preferred_language": None})
    assert resp.status_code == 200
    assert resp.json()["preferred_language"] in [None, ""]


def test_update_user_language_invalid_user(client, db_session):
    resp = client.put("/users/9999/language",
                      json={"preferred_language": "en"})
    assert resp.status_code == 404
