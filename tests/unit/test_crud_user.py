
from backend import crud, models
from tests.people import add_person


def test_update_user_language_none_clears_preference(db_session, seeded_db):
    """Passing None should store NULL, not an empty string."""
    role = db_session.query(models.Role).filter(models.Role.name == "Child").first()
    user = add_person(db_session, "LangKid", role.id)

    # Set a language first
    crud.update_user_language(db_session, user.id, "de")
    db_session.refresh(user)
    assert user.preferred_language == "de"

    # Clear it
    crud.update_user_language(db_session, user.id, None)
    db_session.refresh(user)
    assert user.preferred_language is None


def test_get_user_by_nickname(db_session, seeded_db):
    # Create user
    role = db_session.query(models.Role).filter(
        models.Role.name == "Admin").first()
    add_person(db_session, "Admin", role.id)

    # Get by nickname
    user = crud.get_user_by_nickname(db_session, "Admin")
    assert user is not None
    assert user.id is not None

    # Non-existent
    assert crud.get_user_by_nickname(db_session, "Ghost") is None


def test_get_users_pagination(db_session, seeded_db):
    role = db_session.query(models.Role).first()
    for i in range(5):
        add_person(db_session, f"U{i}", role.id)

    users = crud.get_users(db_session, limit=2)
    assert len(users) == 2

    users_skip = crud.get_users(db_session, skip=2, limit=2)
    assert len(users_skip) == 2
    assert users_skip[0].nickname == "U2"


def test_role_crud(db_session, seeded_db):
    # Get roles
    roles = crud.get_roles(db_session)
    assert len(roles) == 4

    # Get specific role
    role = crud.get_role(db_session, roles[0].id)
    assert role.name == roles[0].name

    # Update multiplier
    updated = crud.update_role_multiplier(db_session, role.id, 2.5)
    assert updated.multiplier_value == 2.5

    db_session.refresh(role)
    assert role.multiplier_value == 2.5

    # Invalid role update
    assert crud.update_role_multiplier(db_session, 9999, 1.0) is None
