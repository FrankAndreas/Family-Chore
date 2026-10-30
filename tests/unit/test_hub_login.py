"""Logging in through the family hub, and the people the hub gives the chores app (spec 2026-10-30). Invented people."""

import pytest
from fastapi.testclient import TestClient

from backend import hub, hub_people, models
from backend.database import get_db
from backend.main import app
from backend.services import scheduler
from tests import fake_hub
from tests.fake_hub import token

ADMIN = "TestAdmin"


def bearer(name):
    return {"Authorization": f"Bearer {token(name)}"}


@pytest.fixture
def family_hub(monkeypatch):
    fake = fake_hub.FakeHub()
    monkeypatch.setattr(fake_hub, "current", fake)
    monkeypatch.setattr(hub, "fetch_session", fake.fetch_session)
    monkeypatch.setattr(hub, "fetch_people", fake.fetch_people)
    fake.add(ADMIN, "PARENT")
    yield fake
    hub.forget()
    hub_people.forget()


@pytest.fixture
def hub_client(db_session, admin_user, family_hub):
    """A client that logs in through the (fake) hub; TestAdmin is a row from before the hub."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def me(client, name=ADMIN):
    return client.get("/users/me", headers=bearer(name))


def role_id(db, name):
    return db.query(models.Role).filter(models.Role.name == name).one().id


def row(db, name):
    db.expire_all()
    return db.query(models.User).filter(models.User.nickname == name).one()


# Logging in


def test_no_login_401(hub_client):
    response = hub_client.get("/users/me")
    assert response.status_code == 401 and response.json()["detail"] == "not_logged_in"


def test_unknown_token_401(hub_client):
    assert hub_client.get("/users/me", headers={"Authorization": "Bearer tok-nobody"}).status_code == 401


def test_me(hub_client):
    found = me(hub_client).json()
    assert (found["nickname"], found["role"]["name"]) == (ADMIN, "Admin")


def test_cookie_needs_the_header_for_changes(hub_client):
    hub_client.cookies.set("hub_session", token(ADMIN))
    refused = hub_client.post("/roles/", json={"name": "Helper", "multiplier_value": 1.1})
    assert refused.status_code == 403 and refused.json()["detail"] == "csrf"
    allowed = hub_client.post(
        "/roles/", json={"name": "Helper", "multiplier_value": 1.1}, headers={"X-Requested-With": "chores"}
    )
    assert allowed.status_code == 200


def test_no_access_403(hub_client, family_hub):
    family_hub.add("Max", "PARENT", access=False)
    response = me(hub_client, "Max")
    assert response.status_code == 403 and response.json()["detail"] == "no_access"


def test_hub_down_503(hub_client, family_hub):
    family_hub.down = True
    response = me(hub_client)
    assert response.status_code == 503 and response.json()["detail"] == "hub_unavailable"


def test_no_login_through_the_tunnel(hub_client):
    response = hub_client.get("/users/me", headers={**bearer(ADMIN), "Cf-Connecting-Ip": "203.0.113.7"})
    assert response.status_code == 401


def test_events_need_a_login(hub_client):
    assert hub_client.get("/events").status_code == 401
    # The short-lived token in the address is gone; the hub cookie is the login
    assert hub_client.get("/events", params={"token": "anything"}).status_code == 401


def test_hub_login_url(hub_client, monkeypatch):
    monkeypatch.setenv("HUB_PUBLIC_URL", "https://home.local.example.ch")
    assert hub_client.get("/hub").json() == {"login_url": "https://home.local.example.ch"}


def test_removed_endpoints(hub_client):
    headers = bearer(ADMIN)
    admin_id = me(hub_client).json()["id"]
    assert hub_client.post("/login/", json={"nickname": ADMIN, "login_pin": "1234"}).status_code in (404, 405)
    created = hub_client.post("/users/", json={"nickname": "X", "login_pin": "1234", "role_id": 1}, headers=headers)
    assert created.status_code in (404, 405)
    assert hub_client.put(f"/users/{admin_id}/password", json={"new_pin": "9999"}, headers=headers).status_code in (
        404,
        405,
    )
    assert hub_client.put(
        f"/users/{admin_id}/language", json={"preferred_language": "en"}, headers=headers
    ).status_code in (404, 405)


# The people from the hub


def test_existing_admin_linked_at_the_switch(hub_client, db_session, family_hub, admin_user):
    admin_user.current_points = 42
    db_session.commit()
    me(hub_client)
    linked = row(db_session, ADMIN)
    assert (linked.id, linked.hub_id, linked.current_points) == (admin_user.id, family_hub.people[ADMIN].id, 42)


def test_linking_needs_the_matching_role(hub_client, db_session, family_hub):
    db_session.add(models.User(nickname="Kid", role_id=role_id(db_session, "Teenager")))
    db_session.add(models.User(nickname="Ana", role_id=role_id(db_session, "Child")))
    db_session.commit()
    family_hub.add("Kid", "CHILD")
    # The hub calls Ana a parent: not the old child row
    family_hub.add("Ana", "PARENT")
    me(hub_client)
    kid = row(db_session, "Kid")
    assert kid.hub_id == family_hub.people["Kid"].id and kid.role.name == "Teenager"
    old_ana = db_session.query(models.User).filter(models.User.hub_id.is_(None)).one()
    assert old_ana.is_active is False


def test_old_rows_linked_by_name_only_at_the_switch(hub_client, db_session, family_hub):
    db_session.add(models.User(nickname="Beat", role_id=role_id(db_session, "Child")))
    db_session.commit()
    me(hub_client)
    family_hub.add("Beat", "CHILD")
    me(hub_client, "Beat")
    rows = db_session.query(models.User).filter(models.User.nickname.like("Beat%")).all()
    assert len(rows) == 2
    assert {r.hub_id is None for r in rows} == {True, False}


def test_roles_follow_the_hub(hub_client, db_session, family_hub):
    family_hub.add("Lena", "CHILD", language="en")
    found = me(hub_client, "Lena").json()
    assert (found["role"]["name"], found["preferred_language"]) == ("Child", "en")
    lena = row(db_session, "Lena")
    # A parent picks the game role of a child here
    lena.role_id = role_id(db_session, "Teenager")
    db_session.commit()
    hub_people.forget()
    assert me(hub_client, "Lena").json()["role"]["name"] == "Teenager"
    family_hub.set_role("Lena", "PARENT")
    assert me(hub_client, "Lena").json()["role"]["name"] == "Admin"
    family_hub.set_role("Lena", "CHILD")
    assert me(hub_client, "Lena").json()["role"]["name"] == "Child"


def test_only_children_get_a_game_role_here(hub_client, db_session, family_hub):
    family_hub.add("Lena", "CHILD")
    family_hub.add("Mia", "PARENT")
    me(hub_client, "Lena")
    me(hub_client, "Mia")
    lena, mia = row(db_session, "Lena"), row(db_session, "Mia")
    put = lambda user_id, body: hub_client.put(f"/users/{user_id}", json=body, headers=bearer(ADMIN))  # noqa: E731
    assert put(lena.id, {"role_id": role_id(db_session, "Teenager")}).status_code == 200
    refused = put(lena.id, {"role_id": role_id(db_session, "Admin")})
    assert refused.status_code == 400 and refused.json()["detail"] == "admin_from_hub"
    refused = put(mia.id, {"role_id": role_id(db_session, "Child")})
    assert refused.status_code == 400 and refused.json()["detail"] == "role_from_hub"
    refused = put(lena.id, {"nickname": "Lea"})
    assert refused.status_code == 400 and refused.json()["detail"] == "name_from_hub"
    assert put(lena.id, {"email": "lena@example.ch"}).status_code == 200


# Removed in the hub: hidden with points and history, until a parent deletes them


def test_removed_person_hidden_and_deleted(hub_client, db_session, family_hub):
    family_hub.add("Lena", "CHILD")
    lena_id = me(hub_client, "Lena").json()["id"]
    refused = hub_client.delete(f"/users/{lena_id}", headers=bearer(ADMIN))
    assert refused.status_code == 409 and refused.json()["detail"] == "still_in_hub"
    family_hub.remove_access("Lena")
    names = [u["nickname"] for u in hub_client.get("/users/", headers=bearer(ADMIN)).json()]
    assert "Lena" not in names
    removed = hub_client.get("/users/removed", headers=bearer(ADMIN)).json()
    assert [u["nickname"] for u in removed] == ["Lena"]
    assert hub_client.delete(f"/users/{lena_id}", headers=bearer(ADMIN)).status_code == 200


def test_removed_person_gets_no_daily_tasks(hub_client, db_session, family_hub):
    family_hub.add("Lena", "CHILD")
    me(hub_client, "Lena")
    family_hub.remove_access("Lena")
    hub_client.get("/users/", headers=bearer(ADMIN))
    task = models.Task(
        name="Tisch decken",
        description="Vor dem Essen",
        base_points=10,
        schedule_type="daily",
        default_due_time="18:00",
    )
    db_session.add(task)
    db_session.commit()
    scheduler.generate_daily_instances(db_session)
    lena = row(db_session, "Lena")
    assert db_session.query(models.TaskInstance).filter(models.TaskInstance.user_id == lena.id).count() == 0
    admin = row(db_session, ADMIN)
    assert db_session.query(models.TaskInstance).filter(models.TaskInstance.user_id == admin.id).count() == 1
