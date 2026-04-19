"""
Streak state-machine for the gamification engine.

Owns all logic related to advancing, resetting, and expiring user streaks.
Mutates User model fields but does NOT commit — the caller is responsible
for transaction boundaries.
"""
from datetime import date, datetime, timedelta, timezone
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from .. import models


def update_user_streak(user: models.User, today: date) -> Tuple[int, bool]:
    """
    Advance or reset the user's streak based on today's date.

    Mutates ``user.current_streak`` and ``user.last_task_date`` in-place
    but does **not** commit.

    Returns:
        (new_streak, is_first_task_today)
    """
    is_first = bool(user.last_task_date != today)

    if is_first:
        if user.last_task_date == today - timedelta(days=1):
            user.current_streak += 1
        else:
            user.current_streak = 1
        user.last_task_date = today

    return int(user.current_streak), is_first


def reset_expired_streaks(db: Session, reference_date: Optional[datetime] = None) -> int:
    """
    Reset ``current_streak`` to 0 for all users who haven't completed a task
    since yesterday.  Intended to run during the midnight cron reset.

    Args:
        db: Active SQLAlchemy session.
        reference_date: Override "now" for testing.  Defaults to UTC now.

    Returns:
        Number of users whose streaks were reset.
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
