from sqlalchemy.orm import Session
from datetime import datetime, date, timezone
from typing import Optional, List
from . import models, schemas, security
from .services.transaction_service import delete_user_transactions, detach_instance_references

# --- User CRUD ---


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_nickname(db: Session, nickname: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.nickname == nickname).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_pin = security.get_password_hash(user.login_pin)
    db_user = models.User(
        nickname=user.nickname,
        login_pin=hashed_pin,
        role_id=user.role_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Re-query to ensure relationships are loaded
    db_user = db.query(models.User).filter(
        models.User.id == db_user.id).first()
    return db_user


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    """Update user profile settings (e.g., email, notifications, nickname, role)."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_password(db: Session, user_id: int, new_pin: str) -> bool:
    """Update user's login PIN."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return False

    hashed_pin = security.get_password_hash(new_pin)
    db_user.login_pin = hashed_pin
    db.commit()
    return True


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user and all related records to satisfy foreign key constraints."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return False

    # Delete related records explicitly
    db.query(models.TaskInstance).filter(models.TaskInstance.user_id == user_id).delete()
    delete_user_transactions(db, user_id)
    db.query(models.Notification).filter(models.Notification.user_id == user_id).delete()
    db.query(models.PushSubscription).filter(models.PushSubscription.user_id == user_id).delete()

    # Finally delete the user
    db.delete(db_user)
    db.commit()
    return True


def update_user_pin(db: Session, user_id: int, hashed_pin: str) -> None:
    """Update a user's PIN to a new hash (used for auto-migration)."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.login_pin = hashed_pin
        db.commit()

# --- Role CRUD ---


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[models.Role]:
    return db.query(models.Role).offset(skip).limit(limit).all()


def get_role(db: Session, role_id: int) -> Optional[models.Role]:
    return db.query(models.Role).filter(models.Role.id == role_id).first()


def update_role_multiplier(db: Session, role_id: int, multiplier: float) -> Optional[models.Role]:
    db_role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if db_role:
        db_role.multiplier_value = multiplier
        db.commit()
        db.refresh(db_role)
    return db_role

# --- Task CRUD ---


def create_task(db: Session, task: schemas.TaskCreate) -> models.Task:
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # Auto-generate instances for the new task so it appears on Family Dashboard immediately
    generate_instances_for_task(db, db_task)

    return db_task


def _generate_instances_for_task(db: Session, task: models.Task, today: datetime) -> int:
    """Shared helper to generate instances for a single task for a given day."""
    created_count = 0
    today_weekday = today.strftime("%A")

    # Skip weekly tasks if today is not the scheduled day
    if task.schedule_type == "weekly":
        if task.default_due_time != today_weekday:
            return 0

    # For recurring tasks, check if cooldown period has elapsed
    if task.schedule_type == "recurring":
        # Find the most recent completion of this task by ANY user
        last_completion = db.query(models.TaskInstance).filter(
            models.TaskInstance.task_id == task.id,
            models.TaskInstance.status == "COMPLETED"
        ).order_by(models.TaskInstance.completed_at.desc()).first()

        if last_completion and last_completion.completed_at:
            completion_date = last_completion.completed_at.date()
            today_date = today.date()
            days_since_completion = (today_date - completion_date).days
            if days_since_completion < task.recurrence_min_days:
                return 0

    # Find target users
    if task.assigned_role_id:
        target_users = db.query(models.User).filter(
            models.User.role_id == task.assigned_role_id).all()
    else:
        target_users = db.query(models.User).all()

    start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)

    for user in target_users:
        # Construct due_time for today
        if task.schedule_type == "daily":
            try:
                hour, minute = map(int, task.default_due_time.split(":"))
                due_time = today.replace(
                    hour=hour, minute=minute, second=0, microsecond=0)
            except ValueError:
                due_time = today.replace(
                    hour=17, minute=0, second=0, microsecond=0)
        else:  # weekly or recurring
            due_time = today.replace(
                hour=23, minute=59, second=0, microsecond=0)

        # Check for existing instance today (start of day to end of day)
        # Deduplication behavior: check regardless of status so we don't duplicate
        # if they completed it and we run a reset again.
        existing = db.query(models.TaskInstance).filter(
            models.TaskInstance.task_id == task.id,
            models.TaskInstance.user_id == user.id,
            models.TaskInstance.due_time >= start_of_day
        ).first()

        if not existing:
            instance = models.TaskInstance(
                task_id=task.id,
                user_id=user.id,
                due_time=due_time,
                status="PENDING"
            )
            db.add(instance)
            created_count += 1

    return created_count


def generate_instances_for_task(db: Session, task: models.Task) -> int:
    """Generate task instances for a single task (for today). Used when creating new tasks."""
    today = datetime.now(timezone.utc)
    count = _generate_instances_for_task(db, task, today)
    db.commit()
    return count


def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[models.Task]:
    return db.query(models.Task).offset(skip).limit(limit).all()


def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate) -> Optional[models.Task]:
    """Update an existing task."""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        return None

    # Update only provided fields
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> bool:
    """Delete a task and all its related instances."""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        return False

    # Get IDs of instances that will be deleted
    instance_ids = [
        inst.id for inst in db.query(models.TaskInstance.id).filter(
            models.TaskInstance.task_id == task_id
        ).all()
    ]

    # B2: Null-out Transaction references to prevent orphaned foreign keys
    if instance_ids:
        detach_instance_references(db, instance_ids)

    # Delete related task instances
    db.query(models.TaskInstance).filter(
        models.TaskInstance.task_id == task_id).delete()

    # Delete the task
    db.delete(db_task)
    db.commit()
    return True


# --- Daily Logic ---
def generate_daily_instances(db: Session) -> int:
    """Generate task instances for daily, weekly, and recurring tasks."""
    # Get all tasks (daily, weekly, and recurring)
    tasks = db.query(models.Task).filter(
        models.Task.schedule_type.in_(["daily", "weekly", "recurring"])
    ).all()

    created_count = 0
    today = datetime.now(timezone.utc)

    for task in tasks:
        created_count += _generate_instances_for_task(db, task, today)

    db.commit()
    return created_count


def get_user_daily_tasks(db: Session, user_id: int) -> List[models.TaskInstance]:
    # Get tasks for today (or all pending/overdue?)
    # Spec says "Daily Task View". Usually implies today's tasks.
    start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return db.query(models.TaskInstance).filter(
        models.TaskInstance.user_id == user_id,
        models.TaskInstance.due_time >= start_of_day,
        models.TaskInstance.status == "PENDING"  # Only show pending tasks
    ).all()


def get_all_pending_tasks(db: Session) -> List[models.TaskInstance]:
    """Get ALL pending tasks for the Family Dashboard."""
    start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return db.query(models.TaskInstance).filter(
        models.TaskInstance.due_time >= start_of_day,
        models.TaskInstance.status == "PENDING"
    ).all()


def get_review_queue(db: Session) -> List[models.TaskInstance]:
    """Get all tasks currently waiting for admin review."""
    return db.query(models.TaskInstance).filter(models.TaskInstance.status == "IN_REVIEW").all()

# --- Reward CRUD ---


def create_reward(db: Session, reward: schemas.RewardCreate) -> models.Reward:
    db_reward = models.Reward(**reward.model_dump())
    db.add(db_reward)
    db.commit()
    db.refresh(db_reward)
    return db_reward


def get_rewards(db: Session, skip: int = 0, limit: int = 100) -> List[models.Reward]:
    return db.query(models.Reward).offset(skip).limit(limit).all()


def update_reward(db: Session, reward_id: int, reward_update: schemas.RewardUpdate) -> Optional[models.Reward]:
    """Update an existing reward."""
    db_reward = db.query(models.Reward).filter(models.Reward.id == reward_id).first()
    if not db_reward:
        return None

    # Update only provided fields
    update_data = reward_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_reward, field, value)

    db.commit()
    db.refresh(db_reward)
    return db_reward


def delete_reward(db: Session, reward_id: int) -> bool:
    """Delete a reward and clear it from any user goals."""
    db_reward = db.query(models.Reward).filter(models.Reward.id == reward_id).first()
    if not db_reward:
        return False

    # Clear goal from any users that have this reward set as their current goal
    db.query(models.User).filter(
        models.User.current_goal_reward_id == reward_id
    ).update({"current_goal_reward_id": None}, synchronize_session="fetch")

    # Delete the reward
    db.delete(db_reward)
    db.commit()
    return True


def set_user_goal(db: Session, user_id: int, reward_id: int) -> Optional[models.User]:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.current_goal_reward_id = reward_id
        db.commit()
        db.refresh(user)
    return user


def get_reward(db: Session, reward_id: int) -> Optional[models.Reward]:
    """Get a reward by ID."""
    return db.query(models.Reward).filter(models.Reward.id == reward_id).first()


# --- Transaction CRUD ---


def get_user_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 100,
                          txn_type: str = None, search: str = None,
                          start_date: datetime = None, end_date: datetime = None) -> List[models.Transaction]:
    """Get transaction history for a specific user with filters."""
    query = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id)

    if txn_type:
        query = query.filter(models.Transaction.type == txn_type)
    if search:
        query = query.filter(
            models.Transaction.description.ilike(f"%{search}%"))
    if start_date:
        query = query.filter(models.Transaction.timestamp >= start_date)
    if end_date:
        query = query.filter(models.Transaction.timestamp <= end_date)

    return query.order_by(models.Transaction.timestamp.desc()).offset(skip).limit(limit).all()


def get_all_transactions(db: Session, skip: int = 0, limit: int = 100,
                         user_id: int = None, txn_type: str = None, search: str = None,
                         start_date: datetime = None, end_date: datetime = None) -> List[models.Transaction]:
    """Get global transaction history with filters."""
    query = db.query(models.Transaction)

    if user_id:
        query = query.filter(models.Transaction.user_id == user_id)
    if txn_type:
        query = query.filter(models.Transaction.type == txn_type)
    if search:
        query = query.filter(
            models.Transaction.description.ilike(f"%{search}%"))
    if start_date:
        query = query.filter(models.Transaction.timestamp >= start_date)
    if end_date:
        query = query.filter(models.Transaction.timestamp <= end_date)

    return query.order_by(models.Transaction.timestamp.desc()).offset(skip).limit(limit).all()


# --- Settings & Language ---


def get_system_setting(db: Session, key: str) -> Optional[models.SystemSettings]:
    return db.query(models.SystemSettings).filter(models.SystemSettings.key == key).first()


def set_system_setting(db: Session, key: str, value: str, description: str = None) -> models.SystemSettings:
    setting = get_system_setting(db, key)
    if setting:
        setting.value = value
        if description:
            setting.description = description
    else:
        setting = models.SystemSettings(
            key=key, value=value, description=description)
        db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting


def update_user_language(db: Session, user_id: int, language: str) -> Optional[models.User]:
    """Update user's preferred language."""
    user = get_user(db, user_id)
    if user:
        user.preferred_language = language
        db.commit()
        db.refresh(user)
    return user


# --- Daily Reset Tracking ---

def get_last_reset_date(db: Session) -> date | None:
    """Get the date of the last daily reset."""
    setting = get_system_setting(db, "last_daily_reset")
    if setting:
        try:
            return datetime.strptime(str(setting.value), "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def set_last_reset_date(db: Session, reset_date: date):
    """Record when the daily reset was performed."""
    set_system_setting(db, "last_daily_reset", reset_date.strftime(
        "%Y-%m-%d"), "Date of last daily task generation")


def is_reset_needed(db: Session) -> bool:
    """Check if a daily reset is needed (last reset was before today)."""
    last_reset = get_last_reset_date(db)
    if last_reset is None:
        return True
    return last_reset < date.today()


def perform_daily_reset_if_needed(db: Session) -> int:
    """Check if reset is needed and perform it. Returns count of created instances."""
    if not is_reset_needed(db):
        return 0

    count = generate_daily_instances(db)
    set_last_reset_date(db, date.today())
    return int(count)


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
