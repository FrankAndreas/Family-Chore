from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from .. import models


from typing import Optional


def reset_expired_streaks(db: Session, reference_date: Optional[datetime] = None) -> int:
    """
    Resets current_streak to 0 for all users who haven't completed a task since yesterday.
    Intended to run during the midnight reset.
    """
    now_date = (reference_date or datetime.now(timezone.utc)).date()
    yesterday = now_date - timedelta(days=1)

    users = db.query(models.User).filter(
        (models.User.last_task_date < yesterday) | (models.User.last_task_date.is_(None)),
        models.User.current_streak > 0
    ).all()

    count = 0
    for user in users:
        user.current_streak = 0
        count += 1

    if count > 0:
        db.commit()
    return count


def award_points_for_task(
    db: Session, instance: models.TaskInstance, current_time: Optional[datetime] = None
) -> models.TaskInstance:
    """
    Shared helper: calculate streaks, daily bonus, award points, create transaction,
    and mark recurring siblings as completed. Commits and refreshes the instance.
    """
    now_dt = current_time or datetime.now(timezone.utc)
    task = instance.task
    user = instance.user
    role = user.role

    # 1. Gamification: Streaks & Daily Bonus
    today_date = now_dt.date()
    is_first_task_today = user.last_task_date != today_date
    daily_bonus = 5 if is_first_task_today else 0

    if is_first_task_today:
        if user.last_task_date == today_date - timedelta(days=1):
            user.current_streak += 1
        else:
            user.current_streak = 1
        user.last_task_date = today_date

    # The streak logic caps at +0.5 bonus. e.g. Day 1: 0, Day 2: 0.1 ... Day 6: 0.5.
    streak_bonus = min(0.5, max(0, user.current_streak - 1) * 0.1)
    effective_multiplier = role.multiplier_value + streak_bonus

    # 2. Calculate Points
    base_points = task.base_points
    awarded_points = int(base_points * effective_multiplier) + daily_bonus

    # 3. Update Instance
    instance.status = "COMPLETED"
    instance.completed_at = now_dt

    # 4. Create Transaction
    desc = f"Completed task: {task.name}"
    if daily_bonus > 0:
        desc += f" (+{daily_bonus} Daily Bonus)"
    if streak_bonus > 0.0:
        desc += f" [Streak: {user.current_streak} days]"

    transaction = models.Transaction(
        user_id=user.id,
        type="EARN",
        base_points_value=base_points,
        multiplier_used=effective_multiplier,
        awarded_points=awarded_points,
        description=desc,
        reference_instance_id=instance.id,
        timestamp=now_dt
    )
    db.add(transaction)

    # 5. Update User Points
    user.current_points += awarded_points
    user.lifetime_points += awarded_points

    # 6. For recurring tasks, mark all other pending instances as completed
    if task.schedule_type == "recurring":
        other_instances = db.query(models.TaskInstance).filter(
            models.TaskInstance.task_id == task.id,
            models.TaskInstance.id != instance.id,
            models.TaskInstance.status == "PENDING"
        ).all()

        for other in other_instances:
            other.status = "COMPLETED"
            other.completed_at = now_dt

    db.commit()
    db.refresh(instance)
    return instance
