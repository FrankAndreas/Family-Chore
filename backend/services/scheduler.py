from sqlalchemy.orm import Session
from datetime import datetime, date, timezone
from typing import Optional

from .. import models
from ..crud import get_system_setting, set_system_setting


def _generate_instances_for_task(
        db: Session, task: models.Task, today: datetime) -> int:
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


def generate_instances_for_task(
        db: Session, task: models.Task, reference_time: Optional[datetime] = None) -> int:
    """Generate task instances for a single task (for today). Used when creating new tasks."""
    today = reference_time or datetime.now(timezone.utc)
    count = _generate_instances_for_task(db, task, today)
    db.commit()
    return count


def generate_daily_instances(
        db: Session, reference_time: Optional[datetime] = None) -> int:
    """Generate task instances for daily, weekly, and recurring tasks."""
    # Get all tasks (daily, weekly, and recurring)
    tasks = db.query(models.Task).filter(
        models.Task.schedule_type.in_(["daily", "weekly", "recurring"])
    ).all()

    created_count = 0
    today = reference_time or datetime.now(timezone.utc)

    for task in tasks:
        created_count += _generate_instances_for_task(db, task, today)

    db.commit()
    return created_count


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


def is_reset_needed(
        db: Session, reference_time: Optional[datetime] = None) -> bool:
    """Check if a daily reset is needed (last reset was before today)."""
    last_reset = get_last_reset_date(db)
    if last_reset is None:
        return True

    today = (reference_time or datetime.now(timezone.utc)).date()
    return last_reset < today


def perform_daily_reset_if_needed(
        db: Session, reference_time: Optional[datetime] = None) -> int:
    """Check if reset is needed and perform it. Returns count of created instances."""
    if not is_reset_needed(db, reference_time):
        return 0

    from .streak_tracker import reset_expired_streaks
    reset_expired_streaks(db, reference_time)

    count = generate_daily_instances(db, reference_time)

    today = (reference_time or datetime.now(timezone.utc)).date()
    set_last_reset_date(db, today)
    return int(count)
