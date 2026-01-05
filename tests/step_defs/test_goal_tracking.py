"""
Step definitions for Goal Tracking BDD scenarios.
"""
from pytest_bdd import scenarios, given, when, then, parsers
from backend import models

# Load scenarios from feature file
scenarios('../features/goal_tracking.feature')


# Shared Given steps

@given("the system is initialized with default roles", target_fixture="seeded_db")
def system_initialized(seeded_db):
    """System has default roles."""
    return seeded_db


# Given steps

@given(parsers.parse('a user "{nickname}" exists with role "{role_name}" and {points:d} points'))
def user_with_points(seeded_db, client, nickname, role_name, points, context):
    """Create user with specific initial points."""
    role = seeded_db.query(models.Role).filter(models.Role.name == role_name).first()

    # Create user directly in DB to set initial points
    user = models.User(
        nickname=nickname,
        login_pin="1234",
        role_id=role.id,
        current_points=points,
        lifetime_points=points
    )
    seeded_db.add(user)
    seeded_db.commit()
    seeded_db.refresh(user)
    context[f'user_{nickname}'] = {"id": user.id, "nickname": user.nickname}


@given(parsers.parse('a reward exists:\n{reward_table}'))
def reward_exists(client, reward_table, context):
    """Create a reward from table data."""
    lines = [line.strip() for line in reward_table.strip().split('\n') if line.strip()]
    data_line = lines[1] if len(lines) > 1 else lines[0]
    parts = [p.strip() for p in data_line.split('|') if p.strip()]

    name = parts[0]
    cost = int(parts[1])
    desc = parts[2]

    response = client.post("/rewards/", json={
        "name": name,
        "cost_points": cost,
        "description": desc,
        "tier_level": 0
    })
    assert response.status_code == 200
    context[f'reward_{name}'] = response.json()


@given(parsers.parse('"{nickname}" has {points:d} current points'))
def set_user_points(seeded_db, nickname, points):
    """Update user's points."""
    user = seeded_db.query(models.User).filter(models.User.nickname == nickname).first()
    user.current_points = points
    seeded_db.commit()


@given(parsers.parse('"{nickname}" has set "{reward_name}" ({cost:d} points) as their goal'))
def user_has_set_goal(client, context, nickname, reward_name, cost):
    """Set a user's goal."""
    user = context[f'user_{nickname}']
    reward = context[f'reward_{reward_name}']

    response = client.post(f"/users/{user['id']}/goal", params={"reward_id": reward['id']})
    assert response.status_code == 200


@given(parsers.parse('a task "{task_name}" with {points:d} base points assigned to "{role_name}"'))
def task_assigned_to_role(seeded_db, client, task_name, points, role_name, context):
    """Create a task assigned to a specific role."""
    role = seeded_db.query(models.Role).filter(models.Role.name == role_name).first()

    response = client.post("/tasks/", json={
        "name": task_name,
        "description": "Test Task",
        "base_points": points,
        "assigned_role_id": role.id,
        "schedule_type": "daily",
        "default_due_time": "17:00"
    })
    assert response.status_code == 200


@given(parsers.parse('the "{role_name}" role has multiplier {multiplier:f}'))
def set_role_multiplier(seeded_db, role_name, multiplier):
    """Set role multiplier."""
    role = seeded_db.query(models.Role).filter(models.Role.name == role_name).first()
    role.multiplier_value = multiplier
    seeded_db.commit()


# When steps

@when(parsers.parse('"{nickname}" sets "{reward_name}" as their goal'))
def set_goal(client, context, nickname, reward_name):
    """User sets a reward as their goal."""
    user = context[f'user_{nickname}']
    reward = context[f'reward_{reward_name}']

    response = client.post(f"/users/{user['id']}/goal", params={"reward_id": reward['id']})
    assert response.status_code == 200
    context['goal_response'] = response.json()


@when("I trigger the daily reset")
def trigger_daily_reset(client):
    """Trigger daily reset."""
    client.post("/daily-reset/")


@when(parsers.parse('"{nickname}" completes their task'))
def complete_task(client, context, nickname):
    """User completes their assigned task."""
    user = context[f'user_{nickname}']
    response = client.get(f"/tasks/daily/{user['id']}")
    tasks = response.json()

    if tasks:
        instance_id = tasks[0]['id']
        client.post(f"/tasks/{instance_id}/complete")


# Then steps

@then(parsers.parse('"{nickname}" should have "{reward_name}" as their current goal'))
def verify_current_goal(seeded_db, nickname, reward_name):
    """Verify user's current goal in DB."""
    user = seeded_db.query(models.User).filter(models.User.nickname == nickname).first()
    assert user.current_goal is not None
    assert user.current_goal.name == reward_name


@then(parsers.parse('the goal should show:\n{table}'))
def verify_goal_metrics(seeded_db, context, table):
    """Verify goal calculation metrics."""
    # This logic would typically be in the frontend, but we verify the backend data supports it
    lines = [line.strip() for line in table.strip().split('\n') if line.strip()]
    data_line = lines[1] if len(lines) > 1 else lines[0]
    parts = [p.strip() for p in data_line.split('|') if p.strip()]

    expected_cost = int(parts[0])
    expected_earned = int(parts[1])
    expected_needed = int(parts[2])

    # Get user from DB to check current state
    # In a real BDD test we might check a "dashboard" endpoint, but checking DB state is fine for backend tests
    user_id = context['user_Teen']['id']
    user = seeded_db.query(models.User).filter(models.User.id == user_id).first()

    assert user.current_goal.cost_points == expected_cost
    assert user.current_points == expected_earned
    assert (user.current_goal.cost_points - user.current_points) == expected_needed


@then(parsers.parse('the progress should be {percent:d} percent'))
def verify_progress_percent(seeded_db, context, percent):
    """Verify progress percentage calculation."""
    user_id = context['user_Teen']['id']
    user = seeded_db.query(models.User).filter(models.User.id == user_id).first()

    if user.current_goal.cost_points > 0:
        calc_percent = min(100, int((user.current_points / user.current_goal.cost_points) * 100))
    else:
        calc_percent = 0

    assert calc_percent == percent


@then(parsers.parse('"{nickname}" should have {points:d} current points'))
def verify_points(seeded_db, nickname, points):
    """Verify user points."""
    user = seeded_db.query(models.User).filter(models.User.nickname == nickname).first()
    assert user.current_points == points


@then(parsers.parse('the goal should show {points:d} points needed'))
def verify_points_needed(seeded_db, context, points):
    """Verify points needed calculation."""
    user_id = context['user_Teen']['id']
    user = seeded_db.query(models.User).filter(models.User.id == user_id).first()
    needed = max(0, user.current_goal.cost_points - user.current_points)
    assert needed == points


@then(parsers.parse('the goal status should be "{status}"'))
def verify_goal_status(seeded_db, context, status):
    """Verify goal status logic."""
    user_id = context['user_Teen']['id']
    user = seeded_db.query(models.User).filter(models.User.id == user_id).first()

    is_ready = user.current_points >= user.current_goal.cost_points
    expected_ready = (status == "READY TO REDEEM")

    assert is_ready == expected_ready
