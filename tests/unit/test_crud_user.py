
from backend import crud, models, schemas


def test_create_user(db_session, seeded_db):
    role = db_session.query(models.Role).filter(
        models.Role.name == "Child").first()

    user_data = schemas.UserCreate(
        nickname="NewKid",
        login_pin="1234",
        role_id=role.id
    )

    user = crud.create_user(db_session, user_data)

    assert user.id is not None
    assert user.nickname == "NewKid"
    assert user.role.name == "Child"
    assert user.current_points == 0


def test_get_user_by_nickname(db_session, seeded_db):
    # Create user
    role = db_session.query(models.Role).filter(
        models.Role.name == "Admin").first()
    crud.create_user(db_session, schemas.UserCreate(
        nickname="Admin", login_pin="0000", role_id=role.id))

    # Get by nickname
    user = crud.get_user_by_nickname(db_session, "Admin")
    assert user is not None
    assert user.id is not None

    # Non-existent
    assert crud.get_user_by_nickname(db_session, "Ghost") is None


def test_get_users_pagination(db_session, seeded_db):
    role = db_session.query(models.Role).first()
    for i in range(5):
        crud.create_user(db_session, schemas.UserCreate(
            nickname=f"U{i}", login_pin="0000", role_id=role.id))

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
