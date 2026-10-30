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


def test_update_user_language_invalid_user(client, db_session):
    resp = client.put("/users/9999/language",
                      json={"preferred_language": "en"})
    assert resp.status_code == 404
