
import pytest
from backend import crud, models, schemas


@pytest.fixture
def reward_setup(db_session, seeded_db):
    # Create test users with different roles
    teen_role = db_session.query(models.Role).filter(models.Role.name == "Teenager").first()
    child_role = db_session.query(models.Role).filter(models.Role.name == "Child").first()

    teen = models.User(nickname="TeenUser", login_pin="1111", role_id=teen_role.id, current_points=1000)
    child = models.User(nickname="ChildUser", login_pin="2222", role_id=child_role.id, current_points=50)

    db_session.add(teen)
    db_session.add(child)

    # Create test rewards
    reward1 = models.Reward(name="Pizza Night", cost_points=500, description="Yum")
    reward2 = models.Reward(name="Toy", cost_points=100, description="Fun")

    db_session.add(reward1)
    db_session.add(reward2)
    db_session.commit()

    return {
        "teen": teen,
        "child": child,
        "pizza": reward1,
        "toy": reward2
    }


def test_create_reward(db_session):
    reward_data = schemas.RewardCreate(
        name="New Reward",
        cost_points=200,
        description="A new shiny thing",
        icon="✨",
        min_lifetime_points=0
    )
    reward = crud.create_reward(db_session, reward_data)
    assert reward.id is not None
    assert reward.name == "New Reward"
    assert reward.cost_points == 200


def test_get_reward(db_session, reward_setup):
    reward = crud.get_reward(db_session, reward_setup["pizza"].id)
    assert reward is not None
    assert reward.name == "Pizza Night"

    # Test non-existent
    assert crud.get_reward(db_session, 9999) is None


def test_get_rewards(db_session, reward_setup):
    rewards = crud.get_rewards(db_session)
    assert len(rewards) == 2
    assert any(r.name == "Pizza Night" for r in rewards)


def test_set_user_goal(db_session, reward_setup):
    user = reward_setup["teen"]
    reward = reward_setup["pizza"]

    updated_user = crud.set_user_goal(db_session, user.id, reward.id)
    assert updated_user.current_goal_reward_id == reward.id

    # Verify persistence
    db_session.refresh(user)
    assert user.current_goal_reward_id == reward.id


def test_redeem_reward_success(db_session, reward_setup):
    user = reward_setup["teen"]  # Has 1000 points
    reward = reward_setup["pizza"]  # Costs 500

    # Set as goal to verify it gets cleared
    user.current_goal_reward_id = reward.id
    db_session.commit()

    result = crud.redeem_reward(db_session, user.id, reward.id)

    assert result["success"] is True
    assert result["points_spent"] == 500
    assert result["remaining_points"] == 500

    # Verify database state
    db_session.refresh(user)
    assert user.current_points == 500
    assert user.current_goal_reward_id is None  # Should be cleared

    # Verify transaction
    tx = db_session.query(models.Transaction).filter(
        models.Transaction.user_id == user.id,
        models.Transaction.type == "REDEEM"
    ).first()
    assert tx is not None
    assert tx.awarded_points == -500
    assert tx.multiplier_used == 1.0


def test_redeem_reward_insufficient_points(db_session, reward_setup):
    user = reward_setup["child"]  # Has 50 points
    reward = reward_setup["pizza"]  # Costs 500

    result = crud.redeem_reward(db_session, user.id, reward.id)

    assert result["success"] is False
    assert "Insufficient points" in result["error"]

    # Verify no points deducted
    db_session.refresh(user)
    assert user.current_points == 50


def test_redeem_reward_invalid_ids(db_session, reward_setup):
    # Invalid user
    result = crud.redeem_reward(db_session, 9999, reward_setup["pizza"].id)
    assert result["success"] is False
    assert result["error"] == "User not found"

    # Invalid reward
    result = crud.redeem_reward(db_session, reward_setup["teen"].id, 9999)
    assert result["success"] is False
    assert result["error"] == "Reward not found"


def test_redeem_reward_split_success(db_session, reward_setup):
    teen = reward_setup["teen"]  # 1000 pts
    child = reward_setup["child"]  # 50 pts
    reward = reward_setup["toy"]   # 100 pts

    contributions = [
        {"user_id": teen.id, "points": 80},
        {"user_id": child.id, "points": 20}
    ]

    result = crud.redeem_reward_split(db_session, reward.id, contributions)

    assert result["success"] is True
    assert result["total_points"] == 100

    # Verify point deductions
    db_session.refresh(teen)
    db_session.refresh(child)
    assert teen.current_points == 1000 - 80
    assert child.current_points == 50 - 20

    # Verify transactions
    tx_teen = db_session.query(models.Transaction).filter(
        models.Transaction.user_id == teen.id,
        models.Transaction.type == "REDEEM"
    ).first()
    assert tx_teen.awarded_points == -80

    tx_child = db_session.query(models.Transaction).filter(
        models.Transaction.user_id == child.id,
        models.Transaction.type == "REDEEM"
    ).first()
    assert tx_child.awarded_points == -20


def test_redeem_reward_split_validation(db_session, reward_setup):
    teen = reward_setup["teen"]
    child = reward_setup["child"]
    reward = reward_setup["toy"]  # 100 pts

    # 1. Total mismatch
    contributions_bad_sum = [
        {"user_id": teen.id, "points": 50},
        {"user_id": child.id, "points": 10}
    ]
    result = crud.redeem_reward_split(db_session, reward.id, contributions_bad_sum)
    assert result["success"] is False
    assert "does not equal reward cost" in result["error"]

    # 2. Insufficient funds individual
    # Child has 50, tries to pay 60
    contributions_too_poor = [
        {"user_id": teen.id, "points": 40},
        {"user_id": child.id, "points": 60}
    ]
    result = crud.redeem_reward_split(db_session, reward.id, contributions_too_poor)
    assert result["success"] is False
    assert "has only 50 pts" in result["error"]

    # 3. Invalid user
    contributions_bad_user = [
        {"user_id": 9999, "points": 100}
    ]
    result = crud.redeem_reward_split(db_session, reward.id, contributions_bad_user)
    assert result["success"] is False
    assert "User 9999 not found" in result["error"]


def test_redeem_reward_split_zero_contribution(db_session, reward_setup):
    """Test that 0 point contributions are ignored."""
    teen = reward_setup["teen"]
    child = reward_setup["child"]
    reward = reward_setup["toy"]  # 100 pts

    contributions = [
        {"user_id": teen.id, "points": 100},
        {"user_id": child.id, "points": 0}  # Should be ignored
    ]

    result = crud.redeem_reward_split(db_session, reward.id, contributions)
    assert result["success"] is True

    # Child should have no transaction
    tx_child = db_session.query(models.Transaction).filter(
        models.Transaction.user_id == child.id,
        models.Transaction.type == "REDEEM"
    ).first()
    assert tx_child is None
