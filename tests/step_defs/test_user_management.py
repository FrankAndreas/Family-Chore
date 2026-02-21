"""
Step definitions for User Management BDD scenarios.
"""

from pytest_bdd import scenarios, given, when, then, parsers
from backend import models

# Load scenarios from feature file
scenarios('../features/user_management.feature')


# Given steps

@given("the system is initialized with default roles", target_fixture="seeded_db")
def system_initialized(seeded_db):
    """System has default roles."""
    return seeded_db


@given(parsers.parse('the following roles exist:\n{roles_table}'))
def roles_exist(seeded_db, roles_table):
    """Verify roles exist in database."""
    # Roles are already created by seeded_db fixture
    pass


@given(parsers.parse('a user exists with:\n{user_table}'))
def user_exists(seeded_db, client, user_table, context):
    """Create a user from table data."""
    lines = [line.strip()
             for line in user_table.strip().split('\n') if line.strip()]
    # Skip header line
    data_line = lines[1] if len(lines) > 1 else lines[0]
    parts = [p.strip() for p in data_line.split('|') if p.strip()]

    nickname = parts[0]
    login_pin = parts[1]
    role_name = parts[2]

    # Get role ID
    role = seeded_db.query(models.Role).filter(
        models.Role.name == role_name).first()

    # Create user via API
    response = client.post("/users/", json={
        "nickname": nickname,
        "login_pin": login_pin,
        "role_id": role.id
    })

    assert response.status_code == 200
    context['created_user'] = response.json()


# When steps

@when(parsers.parse('I create a new user with:\n{user_table}'))
def create_user(seeded_db, client, user_table, context):
    """Create a new user from table data."""
    lines = [line.strip()
             for line in user_table.strip().split('\n') if line.strip()]
    data_line = lines[1] if len(lines) > 1 else lines[0]
    parts = [p.strip() for p in data_line.split('|') if p.strip()]

    nickname = parts[0]
    login_pin = parts[1]
    role_name = parts[2]

    # Get role ID
    role = seeded_db.query(models.Role).filter(
        models.Role.name == role_name).first()

    # Create user via API
    response = client.post("/users/", json={
        "nickname": nickname,
        "login_pin": login_pin,
        "role_id": role.id
    })

    context['response'] = response
    if response.status_code == 200:
        context['created_user'] = response.json()


@when(parsers.parse('I login with nickname "{nickname}" and PIN "{pin}"'))
def login_user(client, nickname, pin, context):
    """Attempt to login with credentials."""
    response = client.post("/login/", json={
        "nickname": nickname,
        "login_pin": pin
    })
    context['login_response'] = response


# Then steps

@then("the user should be created successfully")
def user_created_successfully(context):
    """Verify user was created."""
    assert context['response'].status_code == 200
    assert 'id' in context['created_user']


@then(parsers.parse('the user should have role "{role_name}"'))
def user_has_role(seeded_db, context, role_name):
    """Verify user has the specified role."""
    user = context.get('created_user') or context.get('login_response').json()
    role = seeded_db.query(models.Role).filter(
        models.Role.id == user['role_id']).first()
    assert role.name == role_name


@then(parsers.parse('the user should be assigned to role "{role_name}"'))
def user_assigned_to_role(seeded_db, context, role_name):
    """Verify user is assigned to role."""
    user = context['created_user']
    role = seeded_db.query(models.Role).filter(
        models.Role.id == user['role_id']).first()
    assert role.name == role_name


@then(parsers.parse('the user should have multiplier value {multiplier:f}'))
def user_has_multiplier(seeded_db, context, multiplier):
    """Verify user's role has correct multiplier."""
    user = context.get('created_user') or context.get('login_response').json()
    role = seeded_db.query(models.Role).filter(
        models.Role.id == user['role_id']).first()
    assert role.multiplier_value == multiplier


@then("the login should be successful")
def login_successful(context):
    """Verify login succeeded."""
    assert context['login_response'].status_code == 200


@then("I should receive user details")
def receive_user_details(context):
    """Verify user details are returned."""
    user = context['login_response'].json()
    assert 'id' in user
    assert 'nickname' in user
    assert 'current_points' in user


@then(parsers.parse('the login should fail with error "{error_message}"'))
def login_fails_with_error(context, error_message):
    """Verify login failed with specific error."""
    response = context['login_response']
    assert response.status_code in [401, 404]
    assert error_message in response.json()['detail']
