"""
Step definitions for Role Multiplier BDD scenarios.
"""
from pytest_bdd import scenarios, given, when, then, parsers
from backend import models

# Load scenarios from feature file
scenarios('../features/role_multipliers.feature')


# Shared Given steps

@given("the system is initialized with default roles", target_fixture="seeded_db")
def system_initialized(seeded_db):
    """System has default roles."""
    return seeded_db


# Given steps

@given(parsers.parse('a user "{nickname}" with role "{role_name}" and multiplier {multiplier:f}'))
def user_with_role_and_multiplier(seeded_db, client, nickname, role_name, multiplier, context):
    """Create user and ensure role has specific multiplier."""
    # Set multiplier first
    role = seeded_db.query(models.Role).filter(
        models.Role.name == role_name).first()
    role.multiplier_value = multiplier
    seeded_db.commit()

    # Create user
    response = client.post("/users/", json={
        "nickname": nickname,
        "login_pin": "1234",
        "role_id": role.id
    })
    assert response.status_code == 200
    context[f'user_{nickname}'] = response.json()


@given(parsers.parse('a task "{task_name}" with {points:d} base points assigned to "{role_name}"'))
def task_assigned_to_role(seeded_db, client, task_name, points, role_name, context):
    """Create a task assigned to a specific role."""
    role = seeded_db.query(models.Role).filter(
        models.Role.name == role_name).first()

    response = client.post("/tasks/", json={
        "name": task_name,
        "description": "Test Task",
        "base_points": points,
        "assigned_role_id": role.id,
        "schedule_type": "daily",
        "default_due_time": "17:00"
    })
    assert response.status_code == 200
    context[f'task_{task_name}'] = response.json()


# When steps

@when("I request the list of roles")
def request_roles(client, context):
    """Get all roles."""
    response = client.get("/roles/")
    assert response.status_code == 200
    context['roles_response'] = response.json()


@when(parsers.parse('I update the "{role_name}" role multiplier to {multiplier:f}'))
def update_role_multiplier(seeded_db, client, role_name, multiplier, context):
    """Update a role's multiplier."""
    role = seeded_db.query(models.Role).filter(
        models.Role.name == role_name).first()

    response = client.put(f"/roles/{role.id}", json={
        "multiplier_value": multiplier
    })
    context['update_response'] = response
    if response.status_code == 200:
        context['updated_role'] = response.json()


@when(parsers.parse('I create a daily task instance for "{nickname}"'))
def create_daily_instance(client, context):
    """Trigger daily reset to create instances."""
    response = client.post("/daily-reset/")
    assert response.status_code == 200


@when(parsers.parse('"{nickname}" completes the task'))
def user_completes_task(client, seeded_db, nickname, context):
    """User completes their assigned task."""
    # Find the user's task instance
    user = context[f'user_{nickname}']
    response = client.get(f"/tasks/daily/{user['id']}")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) > 0

    instance_id = tasks[0]['id']

    # Complete it
    response = client.post(f"/tasks/{instance_id}/complete")
    assert response.status_code == 200
    context['completion_response'] = response.json()


# Then steps

@then(parsers.parse('I should see {count:d} roles'))
def see_role_count(context, count):
    """Verify number of roles returned."""
    assert len(context['roles_response']) == count


@then("each role should have a name and multiplier value")
def verify_role_structure(context):
    """Verify role object structure."""
    for role in context['roles_response']:
        assert 'name' in role
        assert 'multiplier_value' in role


@then("the role should be updated successfully")
def role_updated_successfully(context):
    """Verify update was successful."""
    assert context['update_response'].status_code == 200


@then(parsers.parse('the "{role_name}" role should have multiplier value {multiplier:f}'))
def verify_role_multiplier(seeded_db, role_name, multiplier):
    """Verify role multiplier in database."""
    role = seeded_db.query(models.Role).filter(
        models.Role.name == role_name).first()
    # Use approx for float comparison
    assert abs(role.multiplier_value - multiplier) < 0.001


@then(parsers.parse('the update should fail with error "{error_message}"'))
def update_fails_with_error(context, error_message):
    """Verify update failed with specific error."""
    response = context['update_response']
    assert response.status_code == 400
    assert error_message in response.json()['detail']


@then(parsers.parse('"{nickname}" should receive {points:d} points'))
def user_receives_points(seeded_db, nickname, points):
    """Verify user's current points."""
    # Need to refresh user from DB
    user_data = seeded_db.query(models.User).filter(
        models.User.nickname == nickname).first()
    assert user_data.current_points == points


@then(parsers.parse('the transaction should show multiplier {multiplier:f}'))
def transaction_shows_multiplier(seeded_db, context, multiplier):
    """Verify transaction record has correct multiplier."""
    instance_id = context['completion_response']['id']
    transaction = seeded_db.query(models.Transaction).filter(
        models.Transaction.reference_instance_id == instance_id
    ).first()
    assert abs(transaction.multiplier_used - multiplier) < 0.001
