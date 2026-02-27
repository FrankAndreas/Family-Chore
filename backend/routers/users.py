from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from .. import schemas, crud
from ..database import get_db
from ..dependencies import get_current_user, get_current_admin_user
from ..events import broadcaster

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Users"])


@router.post("/users/", response_model=schemas.User, dependencies=[Depends(get_current_admin_user)])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_nickname(db, nickname=user.nickname)
    if db_user:
        raise HTTPException(
            status_code=400, detail="Nickname already registered")
    return crud.create_user(db=db, user=user)


@router.get("/users/", response_model=List[schemas.User], dependencies=[Depends(get_current_user)])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.put("/users/{user_id}", response_model=schemas.User, dependencies=[Depends(get_current_user)])
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    """Update user settings (e.g. email, notifications_enabled)."""
    user = crud.update_user(db, user_id=user_id, user_update=user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users/{user_id}/penalize", dependencies=[Depends(get_current_admin_user)])
async def penalize_user(user_id: int, penalty: schemas.PenaltyRequest, db: Session = Depends(get_db)):
    """Admin endpoint to deduct points from a user."""
    logger.info(
        f"Penalizing user {user_id} for {penalty.points} points: {penalty.reason}")
    result = crud.apply_penalty(db, user_id=user_id, penalty=penalty)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    # Notify User
    crud.create_notification(db, schemas.NotificationCreate(
        user_id=user_id,
        type="SYSTEM",
        title="Points Deducted",
        message=f"You lost {result['points_deducted']} points. Reason: {penalty.reason}"
    ))

    # Broadcast SSE events
    await broadcaster.broadcast("user_penalized", {
        "user_id": user_id,
        "points_deducted": result["points_deducted"],
        "remaining_points": result["remaining_points"],
        "reason": penalty.reason
    })
    await broadcaster.broadcast("notification", {"user_id": user_id})

    return result
