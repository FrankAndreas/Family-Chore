from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, models
from ..database import get_db
from ..dependencies import get_current_user
from ..notifications_service import VAPID_PUBLIC_KEY

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    responses={404: {"description": "Not found"}},
)


@router.get("/push/vapid-public-key", dependencies=[Depends(get_current_user)])
def get_vapid_public_key():
    """Return the VAPID public key for frontend subscription."""
    return {"public_key": VAPID_PUBLIC_KEY}


@router.post("/push/subscribe", response_model=schemas.PushSubscription, dependencies=[Depends(get_current_user)])
def subscribe_push(
    subscription: schemas.PushSubscriptionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a user's push subscription."""
    sub = crud.create_push_subscription(db, user_id=int(current_user.id), sub_in=subscription)
    return sub


@router.delete("/push/unsubscribe", dependencies=[Depends(get_current_user)])
def unsubscribe_push(
    endpoint: str = Body(..., embed=True),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a user's push subscription (only their own)."""
    success = crud.delete_push_subscription_by_user(
        db, endpoint=endpoint, user_id=int(current_user.id)
    )
    if not success:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"success": True}


@router.get("/{user_id}", response_model=List[schemas.Notification])
def read_user_notifications(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notifications for a user (own data or admin)."""
    if current_user.id != user_id and current_user.role.name != "Admin":
        raise HTTPException(status_code=403, detail="Not authorized to view these notifications")
    return crud.get_user_notifications(
        db, user_id=user_id, skip=skip, limit=limit, unread_only=unread_only
    )


@router.post("/{notification_id}/read", response_model=schemas.Notification)
def mark_notification_read(notification_id: int,
                           current_user: models.User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    """Mark a notification as read (uses JWT-derived user identity)."""
    user_id = int(current_user.id)
    notification = crud.mark_notification_read(
        db, notification_id=notification_id, user_id=user_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.post("/read-all", response_model=bool)
def mark_all_read(current_user: models.User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    """Mark all notifications for the current user as read."""
    user_id = int(current_user.id)
    return crud.mark_all_notifications_read(db, user_id=user_id)
