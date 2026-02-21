
from datetime import date, timedelta
from backend import crud, models


def test_system_settings_cycle(db_session):
    # 1. Set new setting
    s = crud.set_system_setting(
        db_session, "theme", "dark", "Theme preference")
    assert s.key == "theme"
    assert s.value == "dark"
    assert s.description == "Theme preference"

    # 2. Get setting
    fetched = crud.get_system_setting(db_session, "theme")
    assert fetched.value == "dark"

    # 3. Update setting
    updated = crud.set_system_setting(db_session, "theme", "light")
    assert updated.value == "light"
    # Description should persist if not provided
    assert updated.description == "Theme preference"


def test_update_user_language(db_session, seeded_db, admin_user):
    # Default is None
    assert admin_user.preferred_language is None

    # Update
    crud.update_user_language(db_session, admin_user.id, "de")

    # Verify
    db_session.refresh(admin_user)
    assert admin_user.preferred_language == "de"

    # Switch back
    crud.update_user_language(db_session, admin_user.id, "en")
    db_session.refresh(admin_user)
    assert admin_user.preferred_language == "en"


def test_daily_reset_logic(db_session, seeded_db):
    # 1. No reset date initially -> Reset Needed
    assert crud.is_reset_needed(db_session) is True

    # 2. Perform reset
    # We need a task to verify it actually does something
    role = seeded_db.query(models.Role).filter(
        models.Role.name == "Contributor").first()
    task = models.Task(name="Daily", description="D", base_points=10,
                       schedule_type="daily", default_due_time="12:00", assigned_role_id=role.id)
    seeded_db.add(task)
    seeded_db.commit()

    # We need a user to assign to
    user = models.User(nickname="U", login_pin="1", role_id=role.id)
    seeded_db.add(user)
    seeded_db.commit()

    count = crud.perform_daily_reset_if_needed(db_session)
    assert count == 1

    # 2. Verify Date recorded
    last_reset = crud.get_last_reset_date(db_session)
    assert last_reset == date.today()

    # 3. Check again -> Should NOT be needed
    assert crud.is_reset_needed(db_session) is False

    # 4. Perform again -> Should do nothing
    count = crud.perform_daily_reset_if_needed(db_session)
    assert count == 0


def test_daily_reset_future_date(db_session):
    # If reset date is tomorrow (time travel?), reset shouldn't happen today
    tomorrow = date.today() + timedelta(days=1)
    crud.set_last_reset_date(db_session, tomorrow)

    assert crud.is_reset_needed(db_session) is False


def test_daily_reset_past_date(db_session):
    # If reset date is yesterday, reset should happen
    yesterday = date.today() - timedelta(days=1)
    crud.set_last_reset_date(db_session, yesterday)

    assert crud.is_reset_needed(db_session) is True
