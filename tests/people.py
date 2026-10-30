"""Family members in the tests: the app has no sign-up any more, people come from the family hub (spec 2026-10-30).
Tests that need someone add them the way the hub sync does: a row with a name and a role."""

from backend import models, schemas


def add_person(db, nickname: str, role_id: int, **fields) -> models.User:
    user = models.User(nickname=nickname, role_id=role_id, current_points=0, lifetime_points=0, **fields)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def add_person_json(db, nickname: str, role_id: int, **fields) -> dict:
    """add_person(), as the API shows the person (what tests read from a response before)."""
    return schemas.User.model_validate(add_person(db, nickname, role_id, **fields)).model_dump(mode="json")
