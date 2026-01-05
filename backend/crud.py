from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas

# --- User CRUD ---


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_nickname(db: Session, nickname: str):
    return db.query(models.User).filter(models.User.nickname == nickname).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    # Note: In a real app, hash the PIN here.
    db_user = models.User(
        nickname=user.nickname,
        login_pin=user.login_pin,
        role_id=user.role_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Re-query to ensure relationships are loaded
    db_user = db.query(models.User).filter(models.User.id == db_user.id).first()
    return db_user

# --- Role CRUD ---


def get_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Role).offset(skip).limit(limit).all()


def get_role(db: Session, role_id: int):
    return db.query(models.Role).filter(models.Role.id == role_id).first()


def update_role_multiplier(db: Session, role_id: int, multiplier: float):
    db_role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if db_role:
        db_role.multiplier_value = multiplier
        db.commit()
        db.refresh(db_role)
    return db_role

# --- Task CRUD ---


def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Task).offset(skip).limit(limit).all()


def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    """Update an existing task."""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        return None

    # Update only provided fields
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    return db_task


# --- Daily Logic ---
def generate_daily_instances(db: Session):
    """Generate task instances for daily, weekly, and recurring tasks."""
    # Get all tasks (daily, weekly, and recurring)
    tasks = db.query(models.Task).filter(
        models.Task.schedule_type.in_(["daily", "weekly", "recurring"])
    ).all()

    created_count = 0
    today = datetime.now()

    today_weekday = today.strftime("%A")  # e.g., "Monday", "Tuesday"

    for task in tasks:
        # Skip weekly tasks if today is not the scheduled day
        if task.schedule_type == "weekly":
            if task.default_due_time != today_weekday:
                continue  # Not the right day for this weekly task

        # For recurring tasks, check if cooldown period has elapsed
        if task.schedule_type == "recurring":
            # Find the most recent completion of this task by ANY user
            last_completion = db.query(models.TaskInstance).filter(
                models.TaskInstance.task_id == task.id,
                models.TaskInstance.status == "COMPLETED"
            ).order_by(models.TaskInstance.completed_at.desc()).first()

            if last_completion and last_completion.completed_at:
                # Check if enough days have passed since the last completion
                # Compare dates, not datetimes, to avoid time-of-day issues
                completion_date = last_completion.completed_at.date()
                today_date = today.date()
                days_since_completion = (today_date - completion_date).days
                if days_since_completion < task.recurrence_min_days:
                    # Still in cooldown period - skip this task
                    continue

        # 2. Find target users
        target_users = []
        if task.assigned_role_id:
            # Task assigned to specific role
            target_users = db.query(models.User).filter(models.User.role_id == task.assigned_role_id).all()
        else:
            # Task not assigned to any role - assign to ALL users (any family member can do it)
            target_users = db.query(models.User).all()

        for user in target_users:
            # 3. Check if instance already exists for today (prevent duplicates)
            # We check if there is an instance for this task/user with due_time today
            # Simple check: due_time is DateTime.

            # Construct due_time for today
            if task.schedule_type == "daily":
                # For daily tasks, parse HH:MM time
                try:
                    hour, minute = map(int, task.default_due_time.split(":"))
                    due_time = today.replace(hour=hour, minute=minute, second=0, microsecond=0)
                except ValueError:
                    # Fallback if time format is bad
                    due_time = today.replace(hour=17, minute=0, second=0, microsecond=0)
            elif task.schedule_type == "weekly":
                # For weekly tasks, set due time to end of day (23:59)
                due_time = today.replace(hour=23, minute=59, second=0, microsecond=0)
            else:  # recurring
                # For recurring tasks, set due time to end of day (23:59)
                due_time = today.replace(hour=23, minute=59, second=0, microsecond=0)

            # Check for existing instance today (start of day to end of day)
            # Only check for PENDING instances - completed ones shouldn't block new ones
            start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
            existing = db.query(models.TaskInstance).filter(
                models.TaskInstance.task_id == task.id,
                models.TaskInstance.user_id == user.id,
                models.TaskInstance.due_time >= start_of_day,
                models.TaskInstance.status == "PENDING"
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

    db.commit()
    return created_count


def get_user_daily_tasks(db: Session, user_id: int):
    # Get tasks for today (or all pending/overdue?)
    # Spec says "Daily Task View". Usually implies today's tasks.
    start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return db.query(models.TaskInstance).filter(
        models.TaskInstance.user_id == user_id,
        models.TaskInstance.due_time >= start_of_day,
        models.TaskInstance.status == "PENDING"  # Only show pending tasks
    ).all()


def complete_task_instance(db: Session, instance_id: int):
    instance = db.query(models.TaskInstance).filter(models.TaskInstance.id == instance_id).first()
    if not instance:
        return None

    if instance.status == "COMPLETED":
        return instance  # Already done

    # 1. Get related data
    task = instance.task
    user = instance.user
    role = user.role

    # 2. Calculate Points
    multiplier = role.multiplier_value
    base_points = task.base_points
    awarded_points = int(base_points * multiplier)

    # 3. Update Instance
    instance.status = "COMPLETED"
    instance.completed_at = datetime.utcnow()

    # 4. Create Transaction
    transaction = models.Transaction(
        user_id=user.id,
        type="EARN",
        base_points_value=base_points,
        multiplier_used=multiplier,
        awarded_points=awarded_points,
        reference_instance_id=instance.id,
        timestamp=datetime.utcnow()
    )
    db.add(transaction)

    # 5. Update User Points
    user.current_points += awarded_points
    user.lifetime_points += awarded_points

    # 6. For recurring tasks, mark all other pending instances as completed
    # This ensures the cooldown applies to all users
    if task.schedule_type == "recurring":
        other_instances = db.query(models.TaskInstance).filter(
            models.TaskInstance.task_id == task.id,
            models.TaskInstance.id != instance.id,
            models.TaskInstance.status == "PENDING"
        ).all()

        for other in other_instances:
            other.status = "COMPLETED"
            other.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(instance)
    return instance

# --- Reward CRUD ---


def create_reward(db: Session, reward: schemas.RewardCreate):
    db_reward = models.Reward(**reward.dict())
    db.add(db_reward)
    db.commit()
    db.refresh(db_reward)
    return db_reward


def get_rewards(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Reward).offset(skip).limit(limit).all()


def set_user_goal(db: Session, user_id: int, reward_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.current_goal_reward_id = reward_id
        db.commit()
        db.refresh(user)
    return user

# --- Settings & Language ---


def get_system_setting(db: Session, key: str):
    return db.query(models.SystemSettings).filter(models.SystemSettings.key == key).first()


def set_system_setting(db: Session, key: str, value: str, description: str = None):
    setting = get_system_setting(db, key)
    if setting:
        setting.value = value
        if description:
            setting.description = description
    else:
        setting = models.SystemSettings(key=key, value=value, description=description)
        db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting


def update_user_language(db: Session, user_id: int, language: str):
    """Update user's preferred language."""
    user = get_user(db, user_id)
    if user:
        user.preferred_language = language
        db.commit()
        db.refresh(user)
    return user
