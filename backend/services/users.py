from sqlalchemy.orm import Session
from datetime import datetime, timezone
from .. import models, schemas
from .. import crud


def apply_penalty(db: Session, user_id: int, penalty: schemas.PenaltyRequest) -> dict:
    """
    Deduct points from a user and create a PENALTY transaction.
    """
    user = crud.get_user(db, user_id)
    if not user:
        return {"success": False, "error": "User not found"}

    # Deduct points (can be negative)
    user.current_points -= penalty.points

    # Create transaction
    transaction = models.Transaction(
        user_id=user.id,
        type="PENALTY",
        base_points_value=penalty.points,
        multiplier_used=1.0,
        awarded_points=-penalty.points,
        description=penalty.reason,
        reference_instance_id=None,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(transaction)
    db.commit()
    db.refresh(user)
    db.refresh(transaction)

    return {
        "success": True,
        "transaction_id": transaction.id,
        "points_deducted": penalty.points,
        "remaining_points": user.current_points
    }
