from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from .. import models


def award_points_for_task(db: Session, instance: models.TaskInstance) -> models.TaskInstance:
    """
    Shared helper: calculate streaks, daily bonus, award points, create transaction,
    and mark recurring siblings as completed. Commits and refreshes the instance.
    """
    task = instance.task
    user = instance.user
    role = user.role

    # 1. Gamification: Streaks & Daily Bonus
    today_date = datetime.now(timezone.utc).date()
    is_first_task_today = user.last_task_date != today_date
    daily_bonus = 5 if is_first_task_today else 0

    if is_first_task_today:
        if user.last_task_date == today_date - timedelta(days=1):
            user.current_streak += 1
        else:
            user.current_streak = 1
        user.last_task_date = today_date

    streak_bonus = min(0.5, max(0, user.current_streak - 1) * 0.1)
    effective_multiplier = role.multiplier_value + streak_bonus

    # 2. Calculate Points
    base_points = task.base_points
    awarded_points = int(base_points * effective_multiplier) + daily_bonus

    # 3. Update Instance
    instance.status = "COMPLETED"
    instance.completed_at = datetime.now(timezone.utc)

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
        timestamp=datetime.now(timezone.utc)
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
            other.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(instance)
    return instance
