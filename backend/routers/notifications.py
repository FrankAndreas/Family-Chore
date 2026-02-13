from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas
from ..database import get_db

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{user_id}", response_model=List[schemas.Notification])
def read_user_notifications(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get notifications for a user."""
    return crud.get_user_notifications(
        db, user_id=user_id, skip=skip, limit=limit, unread_only=unread_only
    )


@router.post("/{notification_id}/read", response_model=schemas.Notification)
def mark_notification_read(notification_id: int, user_id: int, db: Session = Depends(get_db)):
    """Mark a notification as read."""
    notification = crud.mark_notification_read(db, notification_id=notification_id, user_id=user_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.post("/read-all", response_model=bool)
def mark_all_read(user_id: int, db: Session = Depends(get_db)):
    """Mark all notifications for a user as read."""
    return crud.mark_all_notifications_read(db, user_id=user_id)
