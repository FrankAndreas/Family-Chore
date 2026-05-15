from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
from .. import models, schemas
from ..exceptions import UserNotFoundError, RewardNotFoundError, InsufficientPointsError
from .transaction_service import record_redeem


def redeem_reward(
    db: Session, user_id: int, reward_id: int, current_time: Optional[datetime] = None
) -> schemas.RedemptionResponse:
    """
    Redeem a reward for a user.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise UserNotFoundError()

    reward = db.query(models.Reward).filter(
        models.Reward.id == reward_id).first()
    if not reward:
        raise RewardNotFoundError()

    # Validate user has enough points
    if user.current_points < reward.cost_points:
        raise InsufficientPointsError(f"Insufficient points. You have {user.current_points}, need {reward.cost_points}")

    # Deduct points
    user.current_points -= reward.cost_points
    now_dt = current_time or datetime.now(timezone.utc)

    # Create REDEEM transaction (negative awarded_points to indicate spending)
    transaction = record_redeem(
        db,
        user_id=int(user.id),
        cost_points=int(reward.cost_points),
        description=f"Redeemed reward: {reward.name}",
        timestamp=now_dt,
    )

    # If this reward was the user's goal, clear it
    if user.current_goal_reward_id == reward_id:
        user.current_goal_reward_id = None

    db.commit()
    db.refresh(user)
    db.refresh(transaction)

    return schemas.RedemptionResponse(
        success=True,
        transaction_id=int(transaction.id),
        reward_name=str(reward.name),
        points_spent=int(reward.cost_points),
        remaining_points=int(user.current_points),
    )


def redeem_reward_split(
    db: Session, reward_id: int, contributions: list[dict], current_time: Optional[datetime] = None
) -> schemas.SplitRedemptionResponse:
    """
    Redeem a reward by pooling points from multiple users.
    contributions: list of {user_id: int, points: int}
    """
    # Get the reward
    reward = db.query(models.Reward).filter(
        models.Reward.id == reward_id).first()
    if not reward:
        raise RewardNotFoundError()

    # Calculate total contribution
    total_points = sum(c["points"] for c in contributions)
    if total_points != reward.cost_points:
        raise InsufficientPointsError(
            f"Total contribution ({total_points}) does not equal reward cost ({reward.cost_points})")

    # Validate all users exist and have enough points.
    # NOTE: on SQLite writes are serialised so a TOCTOU race here is
    # impossible in practice.  When migrating to Postgres, replace the
    # per-user SELECT with .with_for_update() to acquire row locks before
    # the balance check.
    users_data = []
    for contrib in contributions:
        if contrib["points"] == 0:
            continue  # Skip users with 0 contribution

        user = db.query(models.User).filter(
            models.User.id == contrib["user_id"]).first()
        if not user:
            raise UserNotFoundError(f"User {contrib['user_id']} not found")

        if user.current_points < contrib["points"]:
            raise InsufficientPointsError(
                f"{user.nickname} has only {user.current_points} pts, needs {contrib['points']}")

        users_data.append({"user": user, "points": contrib["points"]})

    # All validations passed - deduct points and create transactions
    transactions = []
    now_dt = current_time or datetime.now(timezone.utc)
    for data in users_data:
        user = data["user"]
        points = data["points"]

        # Deduct points
        user.current_points -= points

        # Create transaction
        transaction = record_redeem(
            db,
            user_id=user.id,
            cost_points=points,
            description=f"Redeemed reward: {reward.name} (Split)",
            timestamp=now_dt,
        )
        db.flush()  # Get transaction ID

        transactions.append(schemas.SplitTransactionDetail(
            user_id=int(user.id),
            user_name=str(user.nickname),
            points=int(points),
            transaction_id=int(transaction.id),
        ))

        # Clear goal if this was user's goal
        if user.current_goal_reward_id == reward_id:
            user.current_goal_reward_id = None

    db.commit()

    return schemas.SplitRedemptionResponse(
        success=True,
        reward_name=str(reward.name),
        total_points=int(total_points),
        transactions=transactions,
    )
