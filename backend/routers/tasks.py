import os
import uuid

from typing import List
import logging

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, File, UploadFile
from sqlalchemy.orm import Session

from .. import schemas, crud, models
from ..database import get_db
from ..dependencies import get_current_user, get_current_admin_user
from ..events import broadcaster
from ..notifications_service import send_email_background, send_push_to_user_background

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Tasks"])


@router.post("/tasks/", response_model=schemas.Task, dependencies=[Depends(get_current_admin_user)])
async def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    logger.info(
        f"Creating task: {task.name} with {task.base_points} base points")
    created_task = crud.create_task(db=db, task=task)
    logger.info(
        f"Task created successfully: {created_task.name} (ID: {created_task.id})")

    # Broadcast SSE event for real-time updates
    await broadcaster.broadcast("task_created", {"task_id": created_task.id, "name": created_task.name})

    return created_task


@router.get("/tasks/", response_model=List[schemas.Task], dependencies=[Depends(get_current_user)])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks


@router.put("/tasks/{task_id}", response_model=schemas.Task, dependencies=[Depends(get_current_admin_user)])
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """Update an existing task."""
    logger.info(f"Updating task: {task_id}")
    updated_task = crud.update_task(
        db, task_id=task_id, task_update=task_update)
    if not updated_task:
        logger.error(f"Task not found: {task_id}")
        raise HTTPException(status_code=404, detail="Task not found")
    logger.info(
        f"Task updated successfully: {updated_task.name} (ID: {updated_task.id})")
    return updated_task


@router.delete("/tasks/{task_id}", dependencies=[Depends(get_current_admin_user)])
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task and all its instances."""
    logger.info(f"Deleting task: {task_id}")
    success = crud.delete_task(db, task_id=task_id)
    if not success:
        logger.error(f"Task not found: {task_id}")
        raise HTTPException(status_code=404, detail="Task not found")
    logger.info(f"Task deleted successfully: {task_id}")

    # Broadcast SSE event for real-time updates
    await broadcaster.broadcast("task_deleted", {"task_id": task_id})

    return {"message": f"Task {task_id} deleted successfully"}


@router.get("/tasks/daily/{user_id}",
            response_model=List[schemas.TaskInstance],
            dependencies=[Depends(get_current_user)])
def read_user_daily_tasks(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_daily_tasks(db, user_id=user_id)


@router.get("/tasks/pending", response_model=List[schemas.TaskInstance], dependencies=[Depends(get_current_user)])
def read_all_pending_tasks(db: Session = Depends(get_db)):
    return crud.get_all_pending_tasks(db)


@router.post("/tasks/{instance_id}/complete",
             response_model=schemas.TaskInstance,
             dependencies=[Depends(get_current_user)])
async def complete_task(
    instance_id: int,
    background_tasks: BackgroundTasks,
    actual_user_id: int = None,
    db: Session = Depends(get_db)
):
    logger.info(
        f"Attempting to complete task instance: {instance_id} (Claimed by user_id: {actual_user_id})")
    try:
        instance = crud.complete_task_instance(
            db, instance_id=instance_id, actual_user_id=actual_user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not instance:
        logger.error(f"Task instance not found: {instance_id}")
        raise HTTPException(status_code=404, detail="Task instance not found")
    logger.info(
        f"Task completed successfully: instance {instance_id} by user {instance.user_id}")

    # Notify User if completed
    if instance.status == "COMPLETED":
        crud.create_notification(db, schemas.NotificationCreate(
            user_id=int(instance.user_id),
            type="TASK_COMPLETED",
            title="Task Completed!",
            message=f"You earned {instance.transaction.awarded_points} points for '{instance.task.name}'."
        ))
    elif instance.status == "IN_REVIEW":
        crud.create_notification(db, schemas.NotificationCreate(
            user_id=int(instance.user_id),
            type="SYSTEM",
            title="Task In Review",
            message=f"Your photo for '{instance.task.name}' is pending admin review."
        ))
        # Send notifications to Admins
        admins = crud.get_notifiable_admins(db)
        for admin in admins:
            send_push_to_user_background(
                background_tasks,
                int(admin.id),
                f"Approval Required: {instance.task.name}",
                f"A photo for '{instance.task.name}' requires your approval."
            )
            if admin.email:
                send_email_background(
                    background_tasks,
                    to_email=str(admin.email),
                    subject=f"Approval Required: {instance.task.name}",
                    body=(
                        f"Hi {admin.nickname},\n\n"
                        f"A photo for the task '{instance.task.name}' has been uploaded by another "
                        "user and requires your approval.\nPlease review it at the God Mode Family Dashboard."
                    )
                )

    # Broadcast SSE event for real-time updates
    await broadcaster.broadcast("task_completed", {"instance_id": instance_id, "user_id": instance.user_id})
    # Broadcast notification event so frontend refreshes list
    await broadcaster.broadcast("notification", {"user_id": instance.user_id})

    return instance


@router.post("/tasks/{instance_id}/upload-photo",
             response_model=schemas.TaskInstance,
             dependencies=[Depends(get_current_user)])
async def upload_task_photo(instance_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a photo for task verification using multipart/form-data."""
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

    instance = db.query(models.TaskInstance).filter(
        models.TaskInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="Task instance not found")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # S4: Derive extension from validated content_type, not user-supplied filename
    content_type_to_ext = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/gif": "gif",
        "image/webp": "webp",
        "image/heic": "heic",
        "image/heif": "heif",
    }
    file_extension = content_type_to_ext.get(file.content_type, "jpg")
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join("uploads", unique_filename)

    # S3: Enforce max upload size while streaming chunks
    total_size = 0
    with open(file_path, "wb") as buffer:
        while content := await file.read(1024 * 1024):  # Read 1MB chunks
            total_size += len(content)
            if total_size > MAX_UPLOAD_SIZE:
                buffer.close()
                os.remove(file_path)
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum upload size is {MAX_UPLOAD_SIZE // (1024 * 1024)} MB."
                )
            buffer.write(content)

    # Set completion_photo_url to the newly served path
    instance.completion_photo_url = f"/uploads/{unique_filename}"
    db.commit()
    db.refresh(instance)

    return instance


@router.get("/tasks/review-queue",
            response_model=List[schemas.TaskInstance],
            dependencies=[Depends(get_current_admin_user)])
def get_review_queue(db: Session = Depends(get_db)):
    """Get all tasks currently waiting for admin review."""
    return crud.get_review_queue(db)


@router.post("/tasks/{instance_id}/review",
             response_model=schemas.TaskInstance,
             dependencies=[Depends(get_current_admin_user)])
async def review_task(
    instance_id: int,
    review: schemas.TaskReviewRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Admin endpoint to approve or reject a task."""
    logger.info(
        f"Reviewing task instance {instance_id}: approved={review.is_approved}")
    instance = crud.review_task_instance(
        db, instance_id=instance_id, review=review)
    if not instance:
        raise HTTPException(
            status_code=404, detail="Task instance not found or not in review")

    # Real-time update
    await broadcaster.broadcast("task_reviewed", {
        "instance_id": instance_id,
        "user_id": instance.user_id,
        "is_approved": review.is_approved
    })
    await broadcaster.broadcast("notification", {"user_id": instance.user_id})

    # Send push notification for review outcome
    outcome = "approved" if review.is_approved else "rejected"
    send_push_to_user_background(
        background_tasks,
        int(instance.user_id),
        f"Task {outcome.title()}",
        f"Your task '{instance.task.name}' was {outcome}."
    )

    return instance
