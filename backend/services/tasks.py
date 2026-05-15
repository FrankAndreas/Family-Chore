from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from .. import models, schemas
from . import gamification
from . import notifications
from ..exceptions import InvalidStateTransitionError, TaskNotFoundError


def complete_task_instance(
    db: Session,
    instance_id: int,
    actual_user_id: int,
    current_time: Optional[datetime] = None,
    skip_ownership_check: bool = False,
) -> schemas.TaskInstance:
    instance = db.query(models.TaskInstance).filter(
        models.TaskInstance.id == instance_id).first()
    if not instance:
        raise TaskNotFoundError()

    if instance.status == "COMPLETED":
        return schemas.TaskInstance.model_validate(instance)  # Already done

    if not skip_ownership_check and instance.user_id != actual_user_id:
        from ..exceptions import AuthorizationError
        raise AuthorizationError("You can only complete tasks assigned to you")

    task = instance.task

    # If the task requires a photo, check if the photo is uploaded
    if task.requires_photo_verification:
        if not instance.completion_photo_url:
            raise InvalidStateTransitionError("Photo upload required before completing this task.")

        # If photo is uploaded, set to IN_REVIEW, no points yet
        instance.status = "IN_REVIEW"
        db.commit()
        db.refresh(instance)
        return schemas.TaskInstance.model_validate(instance)

    return gamification.award_points_for_task(db, instance, current_time)


def review_task_instance(
    db: Session,
    instance_id: int,
    review: schemas.TaskReviewRequest,
    current_time: Optional[datetime] = None
) -> schemas.TaskInstance:
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
        notifications.create_notification(db, schemas.NotificationCreate(
            user_id=int(instance.user_id),
            type="SYSTEM",
            title="Chore Rejected",
            message=(
                f"Your photo for '{instance.task.name}' was rejected. "
                f"Reason: {review.reject_reason or 'No reason provided'}"
            )
        ))

        return schemas.TaskInstance.model_validate(instance)

    # Approved: Award points using gamification service.
    return gamification.award_points_for_task(db, instance, current_time)
