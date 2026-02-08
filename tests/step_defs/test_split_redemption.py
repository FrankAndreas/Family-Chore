"""
Step definitions for Split Redemption BDD scenarios.
"""
from pytest_bdd import scenarios, given, when, then, parsers
from backend import models
from sqlalchemy.orm import Session

# Load scenarios from feature file
scenarios('../features/split_redemption.feature')

# Shared Given steps


@given(parsers.parse('a reward "{name}" costs {cost:d} points'))
def reward_exists(seeded_db: Session, name, cost):
    """Create a reward."""
    reward = models.Reward(
        name=name,
        description="Test Reward",
        cost_points=cost
    )
    seeded_db.add(reward)
    seeded_db.commit()
    seeded_db.refresh(reward)
    return reward


@given(parsers.parse('user "{nickname}" has {points:d} points'))
def user_has_points(seeded_db: Session, nickname, points, context):
    """Create or update a user with specific points."""
    # Check if user exists
    user = seeded_db.query(models.User).filter(
        models.User.nickname == nickname).first()
    if not user:
        # Create a default role if needed
        role = seeded_db.query(models.Role).first()
        if not role:
            role = models.Role(name="Child", multiplier_value=1.0)
            seeded_db.add(role)
            seeded_db.commit()

        user = models.User(
            nickname=nickname,
            login_pin="1234",
            role_id=role.id,
            current_points=points
        )
        seeded_db.add(user)
    else:
        user.current_points = points
        seeded_db.add(user)

    seeded_db.commit()
    seeded_db.refresh(user)
    context[f'user_{nickname}'] = user

# When steps


@when(parsers.parse('they redeem "{reward_name}" splitting {amount:d} points each'))
def redeem_split_even(client, seeded_db, reward_name, amount, context):
    """Execute split redemption with equal amounts."""
    reward = seeded_db.query(models.Reward).filter(
        models.Reward.name == reward_name).first()

    # Identify users from context (Alice and Bob from scenario)
    users = []
    for key, user in context.items():
        if key.startswith('user_'):
            users.append(user)

    contributions = [{"user_id": u.id, "points": amount} for u in users]

    response = client.post(
        f"/rewards/{reward.id}/redeem-split",
        json={"contributions": contributions}
    )
    context['response'] = response


@when(parsers.parse('they attempt to redeem "{reward_name}" contributing {amount:d} points each'))
def attempt_redeem_split_even(client, seeded_db, reward_name, amount, context):
    """Execute split redemption attempt."""
    redeem_split_even(client, seeded_db, reward_name, amount, context)


@when(parsers.parse(
    'they attempt to redeem "{reward_name}" with "{user1}" contributing {amount1:d} '
    'points and "{user2}" contributing {amount2:d} points'
))
def attempt_redeem_split_custom(client, seeded_db, reward_name, user1, amount1, user2, amount2, context):
    """Execute split redemption with custom amounts."""
    reward = seeded_db.query(models.Reward).filter(
        models.Reward.name == reward_name).first()

    u1 = context[f'user_{user1}']
    u2 = context[f'user_{user2}']

    contributions = [
        {"user_id": u1.id, "points": amount1},
        {"user_id": u2.id, "points": amount2}
    ]

    response = client.post(
        f"/rewards/{reward.id}/redeem-split",
        json={"contributions": contributions}
    )
    context['response'] = response

# Then steps


@then("the redemption should be successful")
def redemption_successful(context):
    """Verify success status."""
    assert context['response'].status_code == 200
    data = context['response'].json()
    assert data['success'] is True


@then(parsers.parse('"{nickname}" should have {points:d} points remaining'))
def verify_remaining_points(seeded_db, nickname, points):
    """Verify user points after redemption."""
    # Re-query user to get fresh data
    user = seeded_db.query(models.User).filter(
        models.User.nickname == nickname).first()
    assert user.current_points == points


@then(parsers.parse('the redemption should fail with error "{error_msg}"'))
def redemption_fails_exact(context, error_msg):
    """Verify failure with exact error message."""
    assert context['response'].status_code == 400
    data = context['response'].json()
    assert data['detail'] == error_msg


@then(parsers.parse('the redemption should fail with error containing "{error_fragment}"'))
def redemption_fails_fragment(context, error_fragment):
    """Verify failure with error message fragment."""
    assert context['response'].status_code == 400
    data = context['response'].json()
    assert error_fragment in data['detail']
