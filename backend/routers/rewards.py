from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from .. import schemas, crud
from ..database import get_db
from ..events import broadcaster

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Rewards"])


@router.post("/rewards/", response_model=schemas.Reward)
def create_reward(reward: schemas.RewardCreate, db: Session = Depends(get_db)):
    return crud.create_reward(db=db, reward=reward)


@router.get("/rewards/", response_model=List[schemas.Reward])
def read_rewards(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rewards = crud.get_rewards(db, skip=skip, limit=limit)
    return rewards


@router.put("/rewards/{reward_id}", response_model=schemas.Reward)
def update_reward(reward_id: int, reward: schemas.RewardUpdate, db: Session = Depends(get_db)):
    """Update an existing reward."""
    updated_reward = crud.update_reward(db, reward_id=reward_id, reward_update=reward)
    if not updated_reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    return updated_reward


@router.delete("/rewards/{reward_id}", status_code=204)
def delete_reward(reward_id: int, db: Session = Depends(get_db)):
    """Delete a reward."""
    success = crud.delete_reward(db, reward_id=reward_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reward not found")
    return None


@router.post("/users/{user_id}/goal", response_model=schemas.User)
def set_user_goal(user_id: int, reward_id: int, db: Session = Depends(get_db)):
    user = crud.set_user_goal(db, user_id=user_id, reward_id=reward_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/rewards/{reward_id}/redeem", response_model=schemas.RedemptionResponse)
async def redeem_reward(reward_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Redeem a reward for a user.
    Deducts points, creates a REDEEM transaction, and optionally clears goal.
    """
    logger.info(f"Redeeming reward {reward_id} for user {user_id}")
    result = crud.redeem_reward(db, user_id=user_id, reward_id=reward_id)

    if not result["success"]:
        logger.warning(f"Redemption failed: {result['error']}")
        raise HTTPException(status_code=400, detail=result["error"])

    logger.info(
        f"Redemption successful: {result['reward_name']} for {result['points_spent']} points")

    # Notify User
    crud.create_notification(db, schemas.NotificationCreate(
        user_id=user_id,
        type="REWARD_REDEEMED",
        title="Reward Redeemed!",
        message=f"You redeemed '{result['reward_name']}' for {result['points_spent']} points."
    ))

    # Broadcast SSE event for real-time updates
    await broadcaster.broadcast("reward_redeemed", {
        "user_id": user_id,
        "reward_id": reward_id,
        "reward_name": result["reward_name"],
        "points_spent": result["points_spent"],
        "remaining_points": result["remaining_points"]
    })
    await broadcaster.broadcast("notification", {"user_id": user_id})

    return result


@router.post("/rewards/{reward_id}/redeem-split", response_model=schemas.SplitRedemptionResponse)
async def redeem_reward_split(
    reward_id: int,
    request: schemas.SplitRedemptionRequest,
    db: Session = Depends(get_db)
):
    """
    Redeem a reward by pooling points from multiple users.
    Each contributing user gets their own transaction record.
    """
    logger.info(
        f"Split redemption for reward {reward_id} with {len(request.contributions)} contributors")

    # Convert contributions to list of dicts
    contributions = [{"user_id": c.user_id, "points": c.points}
                     for c in request.contributions]

    result = crud.redeem_reward_split(
        db, reward_id=reward_id, contributions=contributions)

    if not result["success"]:
        logger.warning(f"Split redemption failed: {result['error']}")
        raise HTTPException(status_code=400, detail=result["error"])

    logger.info(
        f"Split redemption successful: {result['reward_name']} for {result['total_points']} points")

    # Broadcast SSE event for real-time updates
    await broadcaster.broadcast("reward_redeemed", {
        "reward_id": reward_id,
        "reward_name": result["reward_name"],
        "total_points": result["total_points"],
        "contributors": result["transactions"],
        "is_split": True
    })

    # Notify all contributors
    for tx in result["transactions"]:
        crud.create_notification(db, schemas.NotificationCreate(
            user_id=tx["user_id"],
            type="REWARD_REDEEMED",
            title="Group Reward Redeemed!",
            message=f"You contributed {tx['points']} points to '{result['reward_name']}'."
        ))
        await broadcaster.broadcast("notification", {"user_id": tx["user_id"]})

    return result
