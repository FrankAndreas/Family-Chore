import pytest
from sqlalchemy.orm import sessionmaker

from backend import models, seed_data as seed_module


@pytest.fixture
def seed(db_session, monkeypatch):
    """Run seed_data() against the test database."""
    monkeypatch.setattr(seed_module, "SessionLocal", sessionmaker(bind=db_session.get_bind()))
    return seed_module.seed_data


def test_seed_creates_the_roles_and_no_people(seed, db_session):
    # People come from the family hub (spec 2026-10-30): no default Admin with a PIN any more
    seed()
    names = {r.name for r in db_session.query(models.Role)}
    assert {"Admin", "Contributor", "Teenager", "Child"} <= names
    assert db_session.query(models.User).count() == 0


def test_seed_is_idempotent(seed, db_session):
    seed()
    seed()
    assert db_session.query(models.Role).filter(models.Role.name == "Admin").count() == 1
