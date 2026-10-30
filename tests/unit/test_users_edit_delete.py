"""What a parent changes about a person here, and deleting the data of someone the family hub removed. Name, login
and parent/child come from the hub (spec 2026-10-30)."""

from fastapi.testclient import TestClient

from backend import models
from tests.people import add_person


def role_id(db_session, name):
    return db_session.query(models.Role).filter(models.Role.name == name).one().id


def test_update_email_and_game_role(client: TestClient, db_session):
    kid = add_person(db_session, "NormalUser", role_id(db_session, "Contributor"))
    res = client.put(f"/users/{kid.id}", json={"email": "kid@example.ch", "role_id": role_id(db_session, "Teenager")})
    assert res.status_code == 200
    assert (res.json()["email"], res.json()["role"]["name"]) == ("kid@example.ch", "Teenager")


def test_name_comes_from_the_hub(client: TestClient, db_session):
    kid = add_person(db_session, "NormalUser", role_id(db_session, "Contributor"))
    res = client.put(f"/users/{kid.id}", json={"nickname": "UpdatedNick"})
    assert res.status_code == 400 and res.json()["detail"] == "name_from_hub"


def test_delete_only_people_removed_in_the_hub(client: TestClient, db_session):
    kid = add_person(db_session, "NormalUser", role_id(db_session, "Contributor"))
    refused = client.delete(f"/users/{kid.id}")
    assert refused.status_code == 409 and refused.json()["detail"] == "still_in_hub"
    kid.is_active = False
    db_session.commit()
    assert client.delete(f"/users/{kid.id}").json()["success"] is True
    assert db_session.get(models.User, kid.id) is None


def test_delete_unknown_person(client: TestClient):
    assert client.delete("/users/99999").status_code == 404
