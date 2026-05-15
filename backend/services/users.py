from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
from .. import schemas
from .. import crud
from ..exceptions import UserNotFoundError
from .transaction_service import record_penalty


def apply_penalty(
    db: Session, user_id: int, penalty: schemas.PenaltyRequest, current_time: Optional[datetime] = None
) -> schemas.PenaltyResponse:
    """
    Deduct points from a user and create a PENALTY transaction.
    """
    user = crud.get_user(db, user_id)
    if not user:
        raise UserNotFoundError()

    new_points = int(user.current_points) - penalty.points
    user.current_points = new_points if new_points > 0 else 0
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

    return schemas.PenaltyResponse(
        success=True,
        transaction_id=int(transaction.id),
        points_deducted=int(penalty.points),
        remaining_points=int(user.current_points),
    )
