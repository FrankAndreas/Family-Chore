"""
Tests for the photo-review state machine in services/tasks.py.

Covers:
- Completing a task that requires photo without uploading → error
- Uploading photo → IN_REVIEW status, no points yet
- Admin approves → COMPLETED, points awarded
- Admin rejects → back to PENDING, photo cleared
- Attempting to review a task not in IN_REVIEW state → error
"""
from datetime import datetime, timezone

import pytest

from backend import models, schemas
from backend.services import tasks as tasks_service
from backend.exceptions import InvalidStateTransitionError, TaskNotFoundError


@pytest.fixture
def photo_setup(db_session, seeded_db):
    """Create a role, user, photo-verification task, and a PENDING instance."""
    role = db_session.query(models.Role).filter(models.Role.name == "Child").first()

    user = models.User(
        nickname="PhotoKid",
        login_pin="0000",
        role_id=role.id,
        current_points=0,
        lifetime_points=0,
    )
    db_session.add(user)
    db_session.commit()

    task = models.Task(
        name="CleanRoom",
        description="Clean your room and take a photo",
        base_points=20,
        assigned_role_id=role.id,
        schedule_type="daily",
        default_due_time="18:00",
        requires_photo_verification=True,
    )
    db_session.add(task)
    db_session.commit()

    instance = models.TaskInstance(
        task_id=task.id,
        user_id=user.id,
        due_time=datetime.now(timezone.utc),
        status="PENDING",
    )
    db_session.add(instance)
    db_session.commit()
    db_session.refresh(instance)

    return {"db": db_session, "user": user, "task": task, "instance": instance}


def test_complete_photo_task_without_photo_raises(photo_setup):
    """Completing a photo-verification task without uploading a photo must raise."""
    s = photo_setup
    with pytest.raises(InvalidStateTransitionError, match="Photo upload required"):
        tasks_service.complete_task_instance(
            s["db"], instance_id=s["instance"].id,
            actual_user_id=s["user"].id,
        )


def test_complete_photo_task_with_photo_goes_to_in_review(photo_setup):
    """After uploading a photo, completing the task sets status to IN_REVIEW, no points."""
    s = photo_setup
    s["instance"].completion_photo_url = "/uploads/fake.webp"
    s["db"].commit()

    result = tasks_service.complete_task_instance(
        s["db"], instance_id=s["instance"].id,
        actual_user_id=s["user"].id,
    )

    assert result.status == "IN_REVIEW"
    s["db"].refresh(s["user"])
    assert s["user"].current_points == 0


def test_approve_review_awards_points(photo_setup):
    """Admin approval of IN_REVIEW task completes it and awards points."""
    s = photo_setup
    s["instance"].completion_photo_url = "/uploads/fake.webp"
    s["instance"].status = "IN_REVIEW"
    s["db"].commit()

    review = schemas.TaskReviewRequest(is_approved=True)
    result = tasks_service.review_task_instance(
        s["db"], instance_id=s["instance"].id, review=review,
        current_time=datetime.now(timezone.utc),
    )

    assert result.status == "COMPLETED"
    s["db"].refresh(s["user"])
    assert s["user"].current_points > 0


def test_reject_review_resets_to_pending_and_clears_photo(photo_setup):
    """Admin rejection resets status to PENDING and clears the photo URL."""
    s = photo_setup
    s["instance"].completion_photo_url = "/uploads/fake.webp"
    s["instance"].status = "IN_REVIEW"
    s["db"].commit()

    review = schemas.TaskReviewRequest(is_approved=False, reject_reason="Too blurry")
    result = tasks_service.review_task_instance(
        s["db"], instance_id=s["instance"].id, review=review,
    )

    assert result.status == "PENDING"
    assert result.completion_photo_url is None
    s["db"].refresh(s["user"])
    assert s["user"].current_points == 0


def test_review_non_in_review_task_raises(photo_setup):
    """Reviewing a task that is not IN_REVIEW must raise InvalidStateTransitionError."""
    s = photo_setup
    # instance is PENDING, not IN_REVIEW
    review = schemas.TaskReviewRequest(is_approved=True)
    with pytest.raises(InvalidStateTransitionError):
        tasks_service.review_task_instance(
            s["db"], instance_id=s["instance"].id, review=review,
        )


def test_review_nonexistent_task_raises(photo_setup):
    review = schemas.TaskReviewRequest(is_approved=True)
    with pytest.raises(TaskNotFoundError):
        tasks_service.review_task_instance(
            photo_setup["db"], instance_id=99999, review=review,
        )
