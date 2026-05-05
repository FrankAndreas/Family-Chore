from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional

from .. import models, schemas


# --- Notification Service Helpers ---

def get_users_with_pending_daily_tasks(db: Session) -> List[models.User]:
    """Find all users who have opted-in to notifications and have pending daily tasks today."""
    start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    # Query users with email and notifications enabled who have pending tasks today
    # Join User -> TaskInstance -> Task explicitly
    users = db.query(models.User).join(
        models.TaskInstance, models.TaskInstance.user_id == models.User.id
    ).join(
        models.Task, models.TaskInstance.task_id == models.Task.id
    ).filter(
        models.User.notifications_enabled.is_(True),
        models.User.email.isnot(None),
        models.TaskInstance.status == "PENDING",
        models.TaskInstance.due_time >= start_of_day,
        models.Task.schedule_type == "daily"
    ).distinct().all()

    return users


def get_notifiable_admins(db: Session) -> List[models.User]:
    """Find all admin users who have opted-in to notifications."""
    # Find all users with "Admin" role, email, and notifications enabled
    users = db.query(models.User).join(models.Role).filter(
        models.Role.name == "Admin",
        models.User.notifications_enabled.is_(True),
        models.User.email.isnot(None)
    ).all()

    return users


# --- Notification CRUD ---

def create_notification(db: Session, notification: schemas.NotificationCreate) -> models.Notification:
    db_notification = models.Notification(**notification.model_dump())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def get_user_notifications(
    db: Session, user_id: int, skip: int = 0, limit: int = 50, unread_only: bool = False
) -> List[models.Notification]:
    query = db.query(models.Notification).filter(
        models.Notification.user_id == user_id)
    if unread_only:
        query = query.filter(models.Notification.read.is_(False))
    return query.order_by(models.Notification.created_at.desc()).offset(skip).limit(limit).all()


# user_id for security check
def mark_notification_read(db: Session, notification_id: int, user_id: int) -> Optional[models.Notification]:
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == user_id
    ).first()
    if notification:
        notification.read = True
        db.commit()
        db.refresh(notification)
    return notification


def mark_all_notifications_read(db: Session, user_id: int) -> bool:
    # Update all unread notifications for this user
    db.query(models.Notification).filter(
        models.Notification.user_id == user_id,
        models.Notification.read.is_(False)
    ).update({"read": True})
    db.commit()
    return True


# --- Push Subscription CRUD ---

def get_push_subscriptions_by_user(db: Session, user_id: int) -> List[models.PushSubscription]:
    return db.query(models.PushSubscription).filter(
        models.PushSubscription.user_id == user_id).all()


def create_push_subscription(
    db: Session, user_id: int, sub_in: schemas.PushSubscriptionCreate
) -> models.PushSubscription:
    # First, check if endpoint already exists (we can just return it or update it)
    existing = db.query(models.PushSubscription).filter(
        models.PushSubscription.endpoint == sub_in.endpoint).first()

    if existing:
        if existing.user_id != user_id:
            existing.user_id = user_id
            db.commit()
            db.refresh(existing)
        return existing

    db_sub = models.PushSubscription(
        user_id=user_id,
        endpoint=sub_in.endpoint,
        p256dh=sub_in.p256dh,
        auth=sub_in.auth
    )
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub


def delete_push_subscription(db: Session, endpoint: str):
    db_sub = db.query(models.PushSubscription).filter(
        models.PushSubscription.endpoint == endpoint).first()
    if db_sub:
        db.delete(db_sub)
        db.commit()
        return True
    return False


def delete_push_subscription_by_user(db: Session, endpoint: str, user_id: int) -> bool:
    """Delete a push subscription only if it belongs to the specified user."""
    db_sub = db.query(models.PushSubscription).filter(
        models.PushSubscription.endpoint == endpoint,
        models.PushSubscription.user_id == user_id
    ).first()
    if db_sub:
        db.delete(db_sub)
        db.commit()
        return True
    return False
