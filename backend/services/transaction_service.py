"""
Centralized Transaction record factory.

This module is the **single owner** of all Transaction creation and cleanup.
Business services (gamification, rewards, penalties) delegate here instead
of constructing ``models.Transaction`` directly.

Design contract:
- Functions create/mutate Transaction records but do **NOT** commit.
- The caller owns the DB transaction boundary (commit/rollback).
- Read-only transaction queries remain in ``crud.py``.
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from .. import models


# ─── Record Factories ──────────────────────────────────────────────


def record_earn(
    db: Session,
    user_id: int,
    base_points: int,
    multiplier: float,
    awarded_points: int,
    description: str,
    reference_instance_id: Optional[int],
    timestamp: datetime,
) -> models.Transaction:
    """
    Create an EARN transaction (task completion, bonuses).

    Does **not** commit — caller must commit.
    """
    transaction = models.Transaction(
        user_id=user_id,
        type="EARN",
        base_points_value=base_points,
        multiplier_used=multiplier,
        awarded_points=awarded_points,
        description=description,
        reference_instance_id=reference_instance_id,
        timestamp=timestamp,
    )
    db.add(transaction)
    return transaction


def record_redeem(
    db: Session,
    user_id: int,
    cost_points: int,
    description: str,
    timestamp: datetime,
    reference_instance_id: Optional[int] = None,
) -> models.Transaction:
    """
    Create a REDEEM transaction (reward redemption).

    ``awarded_points`` is always negative (points spent).
    Does **not** commit — caller must commit.
    """
    transaction = models.Transaction(
        user_id=user_id,
        type="REDEEM",
        base_points_value=cost_points,
        multiplier_used=1.0,
        awarded_points=-cost_points,
        description=description,
        reference_instance_id=reference_instance_id,
        timestamp=timestamp,
    )
    db.add(transaction)
    return transaction


def record_penalty(
    db: Session,
    user_id: int,
    points: int,
    reason: str,
    timestamp: datetime,
) -> models.Transaction:
    """
    Create a PENALTY transaction (admin deduction).

    ``awarded_points`` is always negative.
    Does **not** commit — caller must commit.
    """
    transaction = models.Transaction(
        user_id=user_id,
        type="PENALTY",
        base_points_value=points,
        multiplier_used=1.0,
        awarded_points=-points,
        description=reason,
        reference_instance_id=None,
        timestamp=timestamp,
    )
    db.add(transaction)
    return transaction


# ─── Cleanup Helpers ───────────────────────────────────────────────


def detach_instance_references(db: Session, instance_ids: List[int]) -> int:
    """
    Null-out ``reference_instance_id`` for transactions referencing the
    given TaskInstance IDs.  Used when deleting tasks to prevent orphaned
    foreign keys while preserving audit history.

    Returns the number of updated rows.
    Does **not** commit — caller must commit.
    """
    if not instance_ids:
        return 0
    count = db.query(models.Transaction).filter(
        models.Transaction.reference_instance_id.in_(instance_ids)
    ).update({"reference_instance_id": None}, synchronize_session="fetch")
    return int(count)


def delete_user_transactions(db: Session, user_id: int) -> int:
    """
    Delete all Transaction records for a user.
    Used during cascading user deletion.

    Returns the number of deleted rows.
    Does **not** commit — caller must commit.
    """
    count = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id
    ).delete()
    return int(count)
