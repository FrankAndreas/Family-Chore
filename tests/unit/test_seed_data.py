import pytest
from sqlalchemy.orm import sessionmaker

from backend import models, seed_data as seed_module


@pytest.fixture
def seed(db_session, monkeypatch):
    """Run seed_data() against the test database."""
    monkeypatch.setattr(seed_module, "SessionLocal", sessionmaker(bind=db_session.get_bind()))
    return seed_module.seed_data


def _admins(db_session):
    db_session.expire_all()
    return (db_session.query(models.User).join(models.Role)
            .filter(models.Role.name == "Admin").all())


def test_seed_creates_default_admin_on_empty_database(seed, db_session):
    seed()
    assert [u.nickname for u in _admins(db_session)] == ["Admin"]


def test_seed_is_idempotent(seed, db_session):
    seed()
    seed()
    assert len(_admins(db_session)) == 1


def test_renamed_admin_is_not_recreated(seed, db_session):
    seed()
    admin = _admins(db_session)[0]
    admin.nickname = "Andreas"
    db_session.commit()

    seed()  # e.g. the next container restart
    assert [u.nickname for u in _admins(db_session)] == ["Andreas"]


def test_deleted_default_admin_is_not_recreated_while_another_admin_exists(seed, db_session):
    seed()
    admin_role = db_session.query(models.Role).filter_by(name="Admin").one()
    db_session.add(models.User(nickname="Andreas", login_pin="x", role_id=admin_role.id,
                               current_points=0, lifetime_points=0))
    db_session.delete(db_session.query(models.User).filter_by(nickname="Admin").one())
    db_session.commit()

    seed()
    assert [u.nickname for u in _admins(db_session)] == ["Andreas"]


def test_admin_is_recreated_when_no_admin_is_left(seed, db_session):
    seed()
    child_role = db_session.query(models.Role).filter_by(name="Child").one()
    db_session.query(models.User).filter_by(nickname="Admin").one().role_id = child_role.id
    db_session.commit()

    seed()  # recovery path: no admin left, so a new admin is created under a free name
    assert [u.nickname for u in _admins(db_session)] == ["Admin2"]
