from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone
from typing import Optional, List
from . import models, schemas, security
from .services.transaction_service import delete_user_transactions, detach_instance_references

# --- User CRUD ---


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_nickname(db: Session, nickname: str) -> Optional[models.User]:
    return db.query(models.User).filter(
        models.User.nickname == nickname).first()


def get_users(db: Session, skip: int = 0,
              limit: int = 100) -> List[models.User]:
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
    return db_user


def update_user(db: Session, user_id: int,
                user_update: schemas.UserUpdate) -> Optional[models.User]:
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
    db.query(models.TaskInstance).filter(
        models.TaskInstance.user_id == user_id).delete()
    delete_user_transactions(db, user_id)
    db.query(models.Notification).filter(
        models.Notification.user_id == user_id).delete()
    # PushSubscription is covered by cascade="all, delete-orphan" on User.push_subscriptions

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


def get_roles(db: Session, skip: int = 0,
              limit: int = 100) -> List[models.Role]:
    return db.query(models.Role).offset(skip).limit(limit).all()


def get_role(db: Session, role_id: int) -> Optional[models.Role]:
    return db.query(models.Role).filter(models.Role.id == role_id).first()


def update_role_multiplier(db: Session, role_id: int,
                           multiplier: float) -> Optional[models.Role]:
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
    return db_task


def get_tasks(db: Session, skip: int = 0,
              limit: int = 100) -> List[models.Task]:
    return db.query(models.Task).offset(skip).limit(limit).all()


def update_task(db: Session, task_id: int,
                task_update: schemas.TaskUpdate) -> Optional[models.Task]:
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


def get_user_daily_tasks(
        db: Session, user_id: int) -> List[models.TaskInstance]:
    # Get tasks for today (or all pending/overdue?)
    # Spec says "Daily Task View". Usually implies today's tasks.
    start_of_day = datetime.now(
        timezone.utc).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0)
    return db.query(models.TaskInstance).options(
        joinedload(models.TaskInstance.task),
        joinedload(models.TaskInstance.user)
    ).filter(
        models.TaskInstance.user_id == user_id,
        models.TaskInstance.due_time >= start_of_day,
        models.TaskInstance.status == "PENDING"  # Only show pending tasks
    ).all()


def get_all_pending_tasks(db: Session) -> List[models.TaskInstance]:
    """Get ALL pending tasks for the Family Dashboard."""
    start_of_day = datetime.now(
        timezone.utc).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0)
    return db.query(models.TaskInstance).options(
        joinedload(models.TaskInstance.task),
        joinedload(models.TaskInstance.user)
    ).filter(
        models.TaskInstance.due_time >= start_of_day,
        models.TaskInstance.status == "PENDING"
    ).all()


def get_review_queue(db: Session) -> List[models.TaskInstance]:
    """Get all tasks currently waiting for admin review."""
    return db.query(models.TaskInstance).options(
        joinedload(models.TaskInstance.task),
        joinedload(models.TaskInstance.user)
    ).filter(
        models.TaskInstance.status == "IN_REVIEW"
    ).all()

# --- Reward CRUD ---


def create_reward(db: Session, reward: schemas.RewardCreate) -> models.Reward:
    db_reward = models.Reward(**reward.model_dump())
    db.add(db_reward)
    db.commit()
    db.refresh(db_reward)
    return db_reward


def get_rewards(db: Session, skip: int = 0,
                limit: int = 100) -> List[models.Reward]:
    return db.query(models.Reward).offset(skip).limit(limit).all()


def update_reward(db: Session, reward_id: int,
                  reward_update: schemas.RewardUpdate) -> Optional[models.Reward]:
    """Update an existing reward."""
    db_reward = db.query(
        models.Reward).filter(
        models.Reward.id == reward_id).first()
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
    db_reward = db.query(
        models.Reward).filter(
        models.Reward.id == reward_id).first()
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


def set_user_goal(db: Session, user_id: int,
                  reward_id: int) -> Optional[models.User]:
    reward = db.query(models.Reward).filter(models.Reward.id == reward_id).first()
    if not reward:
        return None
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.current_goal_reward_id = reward_id
        db.commit()
        db.refresh(user)
    return user


def get_reward(db: Session, reward_id: int) -> Optional[models.Reward]:
    """Get a reward by ID."""
    return db.query(models.Reward).filter(
        models.Reward.id == reward_id).first()


# --- Transaction CRUD ---


def get_user_transactions(
        db: Session, user_id: int, skip: int = 0, limit: int = 100,
        txn_type: Optional[str] = None, search: Optional[str] = None,
        start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
) -> List[models.Transaction]:
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

    return query.order_by(models.Transaction.timestamp.desc()
                          ).offset(skip).limit(limit).all()


def get_all_transactions(
        db: Session, skip: int = 0, limit: int = 100,
        user_id: Optional[int] = None, txn_type: Optional[str] = None, search: Optional[str] = None,
        start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
) -> List[models.Transaction]:
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

    return query.order_by(models.Transaction.timestamp.desc()
                          ).offset(skip).limit(limit).all()


# --- Settings & Language ---


def get_system_setting(
        db: Session, key: str) -> Optional[models.SystemSettings]:
    return db.query(models.SystemSettings).filter(
        models.SystemSettings.key == key).first()


def set_system_setting(db: Session, key: str, value: str,
                       description: Optional[str] = None) -> models.SystemSettings:
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


def update_user_language(db: Session, user_id: int,
                         language: str) -> Optional[models.User]:
    """Update user's preferred language."""
    user = get_user(db, user_id)
    if user:
        user.preferred_language = language
        db.commit()
        db.refresh(user)
    return user
