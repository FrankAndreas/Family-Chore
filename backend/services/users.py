from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
from .. import schemas
from .. import crud
from ..exceptions import UserNotFoundError
from .transaction_service import record_penalty


def apply_penalty(
    db: Session, user_id: int, penalty: schemas.PenaltyRequest, current_time: Optional[datetime] = None
) -> dict:
    """
    Deduct points from a user and create a PENALTY transaction.
    """
    user = crud.get_user(db, user_id)
    if not user:
        raise UserNotFoundError()

    # Deduct points (can be negative)
    user.current_points -= penalty.points
    now_dt = current_time or datetime.now(timezone.utc)

    # Create transaction
    transaction = record_penalty(
        db,
        user_id=int(user.id),
        points=penalty.points,
        reason=penalty.reason,
        timestamp=now_dt,
    )
    db.commit()
    db.refresh(user)
    db.refresh(transaction)

    return {
        "success": True,
        "transaction_id": transaction.id,
        "points_deducted": penalty.points,
        "remaining_points": user.current_points
    }
