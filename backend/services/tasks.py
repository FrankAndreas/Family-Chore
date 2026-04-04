from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from .. import models, schemas
from . import gamification
from .. import crud  # fallback for notification creation etc
from ..exceptions import InvalidStateTransitionError, TaskNotFoundError


def complete_task_instance(
    db: Session,
    instance_id: int,
    actual_user_id: int = None,
    current_time: Optional[datetime] = None
) -> models.TaskInstance:
    instance = db.query(models.TaskInstance).filter(
        models.TaskInstance.id == instance_id).first()
    if not instance:
        raise TaskNotFoundError()

    if instance.status == "COMPLETED":
        return instance  # Already done

    # 1. Get related data (and handle reassignment if needed)
    if actual_user_id and actual_user_id != instance.user_id:
        # User B is claiming User A's task
        instance.user_id = actual_user_id
        db.commit()
        db.refresh(instance)

    task = instance.task

    # If the task requires a photo, check if the photo is uploaded
    if task.requires_photo_verification:
        if not instance.completion_photo_url:
            raise InvalidStateTransitionError("Photo upload required before completing this task.")

        # If photo is uploaded, set to IN_REVIEW, no points yet
        instance.status = "IN_REVIEW"
        db.commit()
        db.refresh(instance)
        return instance

    return gamification.award_points_for_task(db, instance, current_time)


def review_task_instance(
    db: Session,
    instance_id: int,
    review: schemas.TaskReviewRequest,
    current_time: Optional[datetime] = None
) -> models.TaskInstance:
    """Admin endpoint to approve or reject a task."""
    instance = db.query(models.TaskInstance).filter(
        models.TaskInstance.id == instance_id).first()
    if not instance:
        raise TaskNotFoundError()

    if instance.status != "IN_REVIEW":
        raise InvalidStateTransitionError(f"Task is not in review state, it is {instance.status}")

    if not review.is_approved:
        # Reject: Send back to pending, clear photo
        instance.status = "PENDING"
        instance.completion_photo_url = None
        db.commit()
        db.refresh(instance)

        # Notify
        crud.create_notification(db, schemas.NotificationCreate(
            user_id=int(instance.user_id),
            type="SYSTEM",
            title="Chore Rejected",
            message=(
                f"Your photo for '{instance.task.name}' was rejected. "
                f"Reason: {review.reject_reason or 'No reason provided'}"
            )
        ))

        return instance

    # Approved: Award points using gamification service.
    return gamification.award_points_for_task(db, instance, current_time)
