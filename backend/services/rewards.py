from sqlalchemy.orm import Session
from datetime import datetime, timezone
from .. import models


def redeem_reward(db: Session, user_id: int, reward_id: int) -> dict:
    """
    Redeem a reward for a user.
    Returns dict with success status, transaction details, or error message.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return {"success": False, "error": "User not found"}

    reward = db.query(models.Reward).filter(
        models.Reward.id == reward_id).first()
    if not reward:
        return {"success": False, "error": "Reward not found"}

    # Validate user has enough points
    if user.current_points < reward.cost_points:
        return {
            "success": False,
            "error": f"Insufficient points. You have {user.current_points}, need {reward.cost_points}"
        }

    # Deduct points
    user.current_points -= reward.cost_points

    # Create REDEEM transaction (negative awarded_points to indicate spending)
    transaction = models.Transaction(
        user_id=user.id,
        type="REDEEM",
        base_points_value=reward.cost_points,
        multiplier_used=1.0,  # No multiplier for redemptions
        awarded_points=-reward.cost_points,  # Negative to show deduction
        description=f"Redeemed reward: {reward.name}",
        reference_instance_id=None,  # No task instance reference
        timestamp=datetime.now(timezone.utc)
    )
    db.add(transaction)

    # If this reward was the user's goal, clear it
    if user.current_goal_reward_id == reward_id:
        user.current_goal_reward_id = None

    db.commit()
    db.refresh(user)
    db.refresh(transaction)

    return {
        "success": True,
        "transaction_id": transaction.id,
        "reward_name": reward.name,
        "points_spent": reward.cost_points,
        "remaining_points": user.current_points
    }


def redeem_reward_split(db: Session, reward_id: int, contributions: list[dict]) -> dict:
    """
    Redeem a reward by pooling points from multiple users.
    contributions: list of {user_id: int, points: int}
    Returns dict with success status, transaction details, or error message.
    """
    # Get the reward
    reward = db.query(models.Reward).filter(
        models.Reward.id == reward_id).first()
    if not reward:
        return {"success": False, "error": "Reward not found"}

    # Calculate total contribution
    total_points = sum(c["points"] for c in contributions)
    if total_points != reward.cost_points:
        return {
            "success": False,
            "error": f"Total contribution ({total_points}) does not equal reward cost ({reward.cost_points})"
        }

    # Validate all users exist and have enough points
    users_data = []
    for contrib in contributions:
        if contrib["points"] == 0:
            continue  # Skip users with 0 contribution

        user = db.query(models.User).filter(
            models.User.id == contrib["user_id"]).first()
        if not user:
            return {"success": False, "error": f"User {contrib['user_id']} not found"}

        if user.current_points < contrib["points"]:
            return {
                "success": False,
                "error": f"{user.nickname} has only {user.current_points} pts, needs {contrib['points']}"
            }

        users_data.append({"user": user, "points": contrib["points"]})

    # All validations passed - deduct points and create transactions
    transactions = []
    for data in users_data:
        user = data["user"]
        points = data["points"]

        # Deduct points
        user.current_points -= points

        # Create transaction
        transaction = models.Transaction(
            user_id=user.id,
            type="REDEEM",
            base_points_value=points,
            multiplier_used=1.0,
            awarded_points=-points,
            description=f"Redeemed reward: {reward.name} (Split)",
            reference_instance_id=None,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(transaction)
        db.flush()  # Get transaction ID

        transactions.append({
            "user_id": user.id,
            "user_name": user.nickname,
            "points": points,
            "transaction_id": transaction.id
        })

        # Clear goal if this was user's goal
        if user.current_goal_reward_id == reward_id:
            user.current_goal_reward_id = None

    db.commit()

    return {
        "success": True,
        "reward_name": reward.name,
        "total_points": total_points,
        "transactions": transactions
    }
