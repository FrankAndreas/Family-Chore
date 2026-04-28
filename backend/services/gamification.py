"""
Gamification orchestrator — thin composition layer.

Delegates calculation to ``points_policy`` and streak management to
``streak_tracker``.  This module's only remaining responsibility is
**persistence**: creating the Transaction, updating the instance, and
committing.

AR2.1 / AR2.2 refactor: the hardcoded math and streak state-machine have
been extracted so that new gamification rules can be added without
modifying this orchestration code.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from .. import models
from .points_policy import calculate_points
from .streak_tracker import update_user_streak
from .transaction_service import record_earn

# ── Re-export so existing callers (tests, cron jobs) are not broken ──
from .streak_tracker import reset_expired_streaks  # noqa: F401


def award_points_for_task(
    db: Session, instance: models.TaskInstance, current_time: Optional[datetime] = None
) -> models.TaskInstance:
    """
    Orchestrate task completion: update streak, calculate points, persist.

    This function composes:
    - ``streak_tracker.update_user_streak`` (streak state-machine)
    - ``points_policy.calculate_points``  (pure math)

    And then handles only persistence concerns (Transaction, User points, commit).
    """
    now_dt = current_time or datetime.now(timezone.utc)
    task = instance.task
    user = instance.user
    role = user.role

    # 1. Streak (delegated to streak_tracker)
    streak, is_first = update_user_streak(user, now_dt.date())

    # 2. Points (delegated to points_policy — pure, no side effects)
    breakdown = calculate_points(
        base_points=task.base_points,
        role_multiplier=role.multiplier_value,
        current_streak=streak,
        is_first_task_today=is_first,
    )

    # 3. Persistence — the only responsibility left here
    instance.status = "COMPLETED"
    instance.completed_at = now_dt

    desc = f"Completed task: {task.name}"
    if breakdown.description_suffix:
        desc += f" {breakdown.description_suffix}"

    record_earn(
        db,
        user_id=user.id,
        base_points=breakdown.base_points,
        multiplier=breakdown.effective_multiplier,
        awarded_points=breakdown.total_awarded,
        description=desc,
        reference_instance_id=int(instance.id),
        timestamp=now_dt,
    )

    # Update user totals
    user.current_points += breakdown.total_awarded
    user.lifetime_points += breakdown.total_awarded

    # For recurring tasks, mark all other pending instances as completed
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
