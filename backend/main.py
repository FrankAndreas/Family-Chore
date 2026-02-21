from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from contextlib import asynccontextmanager
import logging
import asyncio
import json
import datetime
from datetime import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from . import models, schemas, crud
from .database import engine, get_db, SessionLocal
from .routers import analytics, notifications
from .migrations.manager import MigrationManager
from .backup import BackupManager


# Initialize Tables
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# SSE: Event broadcasting system
class EventBroadcaster:
    def __init__(self):
        self.clients: List[asyncio.Queue] = []

    async def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self.clients.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        if queue in self.clients:
            self.clients.remove(queue)

    async def broadcast(self, event_type: str, data: dict = None):
        """Broadcast event to all connected clients."""
        message = {"type": event_type, "data": data}
        for queue in self.clients:
            await queue.put(message)
        logger.info(f"SSE broadcast: {event_type} to {len(self.clients)} clients")


broadcaster = EventBroadcaster()


# Background scheduler for midnight reset
scheduler = BackgroundScheduler()


def scheduled_daily_reset():
    """Scheduled job that runs at midnight to generate daily task instances."""
    logger.info("Midnight scheduler: Running daily reset...")
    try:
        db = SessionLocal()
        count = crud.perform_daily_reset_if_needed(db)
        if count > 0:
            logger.info(f"Midnight scheduler: Generated {count} task instances")
        else:
            logger.info("Midnight scheduler: No new instances needed")
        db.close()
    except Exception as e:
        logger.error(f"Midnight scheduler failed: {e}")


backup_manager = BackupManager()


def run_backup_job():
    """Wrapper to run backup from scheduler"""
    logger.info("Running scheduled backup...")
    try:
        backup_path = backup_manager.create_backup()
        logger.info(f"Backup created: {backup_path}")
        deleted = backup_manager.cleanup_old_backups(retention_days=7)
        if deleted:
            logger.info(f"Cleaned up {len(deleted)} old backups.")
    except Exception as e:
        logger.error(f"Backup job failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    # 1. Run migrations first to ensure schema is up-to-date
    MigrationManager.run_migrations()

    # 2. Ensure tables exist (will create new tables if any)
    models.Base.metadata.create_all(bind=engine)
    # Seed initial data
    try:
        from .seed_data import seed_data
        seed_data()
    except Exception as e:
        logger.error(f"Failed to seed data: {e}")

    # Smart daily reset: Only generate if not already done today
    try:
        db = SessionLocal()
        count = crud.perform_daily_reset_if_needed(db)
        if count > 0:
            logger.info(f"Startup: Generated {count} task instances for today")
        else:
            logger.info("Startup: Daily reset already performed today, skipping")
        db.close()
    except Exception as e:
        logger.error(f"Failed to generate daily instances on startup: {e}")

    # Fetch system timezone (default to Europe/Berlin)
    timezone_str = "Europe/Berlin"
    try:
        db = SessionLocal()
        setting = crud.get_system_setting(db, "default_timezone")
        if setting:
            timezone_str = setting.value
        else:
            # Create default if not exists
            crud.set_system_setting(db, "default_timezone", timezone_str, "System-wide timezone for scheduler")
        db.close()
    except Exception as e:
        logger.error(f"Failed to fetch timezone setting: {e}")

    logger.info(f"Configuring scheduler with timezone: {timezone_str}")
    scheduler.configure(timezone=timezone_str)

    # Start the midnight scheduler
    scheduler.add_job(
        scheduled_daily_reset,
        trigger=CronTrigger(hour=0, minute=0, timezone=timezone_str),  # Run at midnight local time
        id="daily_reset_job",
        replace_existing=True
    )

    # Schedule Daily Backup (02:00 AM)
    scheduler.add_job(
        run_backup_job,
        trigger=CronTrigger(hour=2, minute=0, timezone=timezone_str),
        id="daily_backup_job",
        replace_existing=True
    )

    scheduler.start()
    logger.info("Midnight scheduler started - daily reset will run at 00:00, backups at 02:00")

    yield  # Application runs here

    # --- Shutdown ---
    logger.info("Initiating application shutdown...")
    try:
        if scheduler.running:
            logger.info("Shutting down scheduler (waiting for active jobs)...")
            scheduler.shutdown(wait=False)
            logger.info("Scheduler shut down successfully.")
        else:
            logger.info("Scheduler was not running.")
    except Exception as e:
        logger.error(f"Error during scheduler shutdown: {e}")
    logger.info("Application shutdown complete.")


app = FastAPI(title="ChoreSpec MVP", lifespan=lifespan)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:5174",  # Vite dev server (alt)
        "http://localhost:3000",  # Alternative React dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analytics.router)
app.include_router(notifications.router)


@app.post("/backups/run")
def trigger_manual_backup():
    """Manually trigger a backup in the background."""
    run_backup_job()
    return {"status": "Backup completed"}


# --- SSE Endpoint ---
@app.get("/events")
async def sse_events():
    """Server-Sent Events endpoint for real-time updates."""
    async def event_stream():
        queue = await broadcaster.subscribe()
        try:
            # Send initial connection confirmation
            yield f"data: {json.dumps({'type': 'connected'})}\n\n"

            while True:
                # Wait for new events (with timeout for keepalive)
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(message)}\n\n"
                except asyncio.TimeoutError:
                    # Send keepalive ping
                    yield f"data: {json.dumps({'type': 'ping'})}\n\n"
        finally:
            broadcaster.unsubscribe(queue)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


# Dependency


@app.get("/")
def read_root():
    return {"message": "Welcome to ChoreSpec API"}


# --- User Endpoints ---


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_nickname(db, nickname=user.nickname)
    if db_user:
        raise HTTPException(status_code=400, detail="Nickname already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.post("/login/", response_model=schemas.User)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for user: {user_credentials.nickname}")
    user = crud.get_user_by_nickname(db, nickname=user_credentials.nickname)
    if not user:
        logger.warning(f"Login failed - user not found: {user_credentials.nickname}")
        raise HTTPException(status_code=404, detail="User not found")
    if user.login_pin != user_credentials.login_pin:
        logger.warning(f"Login failed - incorrect PIN for user: {user_credentials.nickname}")
        raise HTTPException(status_code=401, detail="Incorrect PIN")
    logger.info(f"Login successful for user: {user_credentials.nickname} (ID: {user.id})")
    return user


# --- Role Endpoints ---


@app.post("/roles/", response_model=schemas.Role)
def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    """Create a new role."""
    logger.info(f"Creating role: {role.name} with multiplier {role.multiplier_value}")
    # Check if role name already exists
    existing = db.query(models.Role).filter(models.Role.name == role.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role with this name already exists")

    if role.multiplier_value < 0.1:
        raise HTTPException(status_code=400, detail="Multiplier must be >= 0.1")

    db_role = models.Role(name=role.name, multiplier_value=role.multiplier_value)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    logger.info(f"Role created: {db_role.name} (ID: {db_role.id})")
    return db_role


@app.get("/roles/", response_model=List[schemas.Role])
def read_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    roles = crud.get_roles(db, skip=skip, limit=limit)
    return roles


@app.get("/roles/{role_id}/users")
def get_role_users(role_id: int, db: Session = Depends(get_db)):
    """Get count of users assigned to a role."""
    users = db.query(models.User).filter(models.User.role_id == role_id).all()
    return {"count": len(users), "users": [{"id": u.id, "nickname": u.nickname} for u in users]}


@app.put("/roles/{role_id}", response_model=schemas.Role)
def update_role(role_id: int, role_update: schemas.RoleUpdate, db: Session = Depends(get_db)):
    db_role = crud.get_role(db, role_id=role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Validation (AC 2.4)
    if role_update.multiplier_value < 0.1:
        raise HTTPException(status_code=400, detail="Multiplier must be >= 0.1")

    return crud.update_role_multiplier(db, role_id=role_id, multiplier=role_update.multiplier_value)


@app.delete("/roles/{role_id}")
def delete_role(role_id: int, reassign_to_role_id: int = None, db: Session = Depends(get_db)):
    """Delete a role. If users are assigned, reassign_to_role_id must be provided."""
    logger.info(f"Deleting role: {role_id}, reassign to: {reassign_to_role_id}")

    db_role = crud.get_role(db, role_id=role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Check if users are assigned to this role
    users_with_role = db.query(models.User).filter(models.User.role_id == role_id).all()

    if users_with_role:
        if not reassign_to_role_id:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete role: {len(users_with_role)} users are assigned. Provide reassign_to_role_id."
            )

        # Validate target role exists
        target_role = crud.get_role(db, role_id=reassign_to_role_id)
        if not target_role:
            raise HTTPException(status_code=400, detail="Target role for reassignment not found")

        # Reassign all users
        for user in users_with_role:
            user.role_id = reassign_to_role_id
        db.commit()
        logger.info(f"Reassigned {len(users_with_role)} users from role {role_id} to {reassign_to_role_id}")

    # Also update tasks assigned to this role
    tasks_with_role = db.query(models.Task).filter(models.Task.assigned_role_id == role_id).all()
    for task in tasks_with_role:
        task.assigned_role_id = None  # Set to "All Family Members"
    db.commit()

    # Delete the role
    db.delete(db_role)
    db.commit()
    logger.info(f"Role deleted: {role_id}")

    return {
        "message": f"Role deleted successfully. "
        f"{len(users_with_role)} users reassigned, {len(tasks_with_role)} tasks updated."
    }


# --- Task Endpoints ---


@app.post("/tasks/", response_model=schemas.Task)
async def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating task: {task.name} with {task.base_points} base points")
    created_task = crud.create_task(db=db, task=task)
    logger.info(f"Task created successfully: {created_task.name} (ID: {created_task.id})")

    # Broadcast SSE event for real-time updates
    await broadcaster.broadcast("task_created", {"task_id": created_task.id, "name": created_task.name})

    return created_task


@app.get("/tasks/", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks


@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """Update an existing task."""
    logger.info(f"Updating task: {task_id}")
    updated_task = crud.update_task(db, task_id=task_id, task_update=task_update)
    if not updated_task:
        logger.error(f"Task not found: {task_id}")
        raise HTTPException(status_code=404, detail="Task not found")
    logger.info(f"Task updated successfully: {updated_task.name} (ID: {updated_task.id})")
    return updated_task


@app.delete("/tasks/{task_id}")
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


@app.get("/tasks/export", response_model=schemas.TasksExport)
def export_tasks(db: Session = Depends(get_db)):
    """Export all tasks in a human-readable format for backup or AI generation."""
    logger.info("Exporting all tasks...")
    tasks = crud.get_tasks(db)

    # Build role name lookup
    roles = {r.id: r.name for r in crud.get_roles(db)}

    export_items = []
    for task in tasks:
        export_items.append(schemas.TaskExportItem(
            name=task.name,
            description=task.description,
            base_points=task.base_points,
            assigned_role=roles.get(task.assigned_role_id) if task.assigned_role_id else None,
            schedule_type=task.schedule_type,
            default_due_time=task.default_due_time,
            recurrence_min_days=task.recurrence_min_days,
            recurrence_max_days=task.recurrence_max_days,
            requires_photo_verification=bool(task.requires_photo_verification),
        ))

    logger.info(f"Exported {len(export_items)} tasks")
    return schemas.TasksExport(
        version="1.0",
        exported_at=datetime.datetime.now(timezone.utc).isoformat(),
        tasks=export_items
    )


@app.post("/tasks/import")
async def import_tasks(import_data: schemas.TasksImport, db: Session = Depends(get_db)):
    """Import tasks from a structured format. Uses role names instead of IDs."""
    logger.info(f"Importing {len(import_data.tasks)} tasks...")

    # Build role name to ID lookup
    roles = {r.name.lower(): r.id for r in crud.get_roles(db)}

    # Add localized aliases (German -> English System Roles)
    role_aliases = {
        "kind": "child",
        "teenager": "teenager",  # Same
        "mitwirkender": "contributor",
        "administrator": "admin",
        "elternteil": "admin",  # Map Parent/Elternteil to Admin or specific role if exists? Seed data has Admin.
        "partner": "contributor",  # Default assumption
    }

    # Merge aliases into lookup
    for alias, target in role_aliases.items():
        if target in roles:
            roles[alias] = roles[target]

    # Get existing task names for duplicate detection
    existing_names = {t.name.lower() for t in crud.get_tasks(db)}

    created = []
    skipped = []
    errors = []

    for i, task_item in enumerate(import_data.tasks):
        try:
            # Check for duplicates
            if task_item.name.lower() in existing_names:
                if import_data.skip_duplicates:
                    skipped.append(task_item.name)
                    continue
                else:
                    errors.append(f"Task '{task_item.name}' already exists")
                    continue

            # Resolve role name to ID
            assigned_role_id = None
            if task_item.assigned_role:
                role_name_lower = task_item.assigned_role.lower()
                if role_name_lower not in roles:
                    errors.append(f"Task '{task_item.name}': Unknown role '{task_item.assigned_role}'")
                    continue
                assigned_role_id = roles[role_name_lower]

            # Create the task using existing schema
            task_create = schemas.TaskCreate(
                name=task_item.name,
                description=task_item.description,
                base_points=task_item.base_points,
                assigned_role_id=assigned_role_id,
                schedule_type=task_item.schedule_type,
                default_due_time=task_item.default_due_time,
                recurrence_min_days=task_item.recurrence_min_days,
                recurrence_max_days=task_item.recurrence_max_days,
                requires_photo_verification=task_item.requires_photo_verification is True,
            )
            new_task = crud.create_task(db=db, task=task_create)
            created.append(new_task.name)
            existing_names.add(task_item.name.lower())  # Prevent duplicates within import
            logger.info(f"Imported task: {new_task.name} (ID: {new_task.id})")

        except Exception as e:
            errors.append(f"Task '{task_item.name}': {str(e)}")

    # Broadcast SSE event if any tasks were created
    if created:
        await broadcaster.broadcast("tasks_imported", {"count": len(created)})

    logger.info(f"Import complete: {len(created)} created, {len(skipped)} skipped, {len(errors)} errors")

    return {
        "success": len(errors) == 0,
        "created": created,
        "skipped": skipped,
        "errors": errors,
        "summary": f"Created {len(created)} tasks, skipped {len(skipped)}, {len(errors)} errors"
    }


@app.post("/daily-reset/")
def trigger_daily_reset(db: Session = Depends(get_db)):
    logger.info("Triggering daily reset...")
    count = crud.generate_daily_instances(db)
    logger.info(f"Daily reset complete. Created {count} task instances.")
    return {"message": f"Daily reset complete. Created {count} task instances."}


@app.get("/tasks/daily/{user_id}", response_model=List[schemas.TaskInstance])
def read_user_daily_tasks(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_daily_tasks(db, user_id=user_id)


@app.get("/tasks/pending", response_model=List[schemas.TaskInstance])
def read_all_pending_tasks(db: Session = Depends(get_db)):
    return crud.get_all_pending_tasks(db)


@app.post("/tasks/{instance_id}/complete", response_model=schemas.TaskInstance)
async def complete_task(instance_id: int, actual_user_id: int = None, db: Session = Depends(get_db)):
    logger.info(f"Attempting to complete task instance: {instance_id} (Claimed by user_id: {actual_user_id})")
    try:
        instance = crud.complete_task_instance(db, instance_id=instance_id, actual_user_id=actual_user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not instance:
        logger.error(f"Task instance not found: {instance_id}")
        raise HTTPException(status_code=404, detail="Task instance not found")
    logger.info(f"Task completed successfully: instance {instance_id} by user {instance.user_id}")

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

    # Broadcast SSE event for real-time updates
    await broadcaster.broadcast("task_completed", {"instance_id": instance_id, "user_id": instance.user_id})
    # Broadcast notification event so frontend refreshes list
    await broadcaster.broadcast("notification", {"user_id": instance.user_id})

    return instance


@app.post("/tasks/{instance_id}/upload-photo", response_model=schemas.TaskInstance)
async def upload_task_photo(instance_id: int, body: schemas.PhotoUploadRequest, db: Session = Depends(get_db)):
    """Upload a photo URL for task verification."""
    instance = db.query(models.TaskInstance).filter(models.TaskInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="Task instance not found")

    instance.completion_photo_url = body.photo_url
    db.commit()
    db.refresh(instance)

    return instance


@app.get("/tasks/review-queue", response_model=List[schemas.TaskInstance])
def get_review_queue(db: Session = Depends(get_db)):
    """Get all tasks currently waiting for admin review."""
    return crud.get_review_queue(db)


@app.post("/tasks/{instance_id}/review", response_model=schemas.TaskInstance)
async def review_task(instance_id: int, review: schemas.TaskReviewRequest, db: Session = Depends(get_db)):
    """Admin endpoint to approve or reject a task."""
    logger.info(f"Reviewing task instance {instance_id}: approved={review.is_approved}")
    instance = crud.review_task_instance(db, instance_id=instance_id, review=review)
    if not instance:
        raise HTTPException(status_code=404, detail="Task instance not found or not in review")

    # Real-time update
    await broadcaster.broadcast("task_reviewed", {
        "instance_id": instance_id,
        "user_id": instance.user_id,
        "is_approved": review.is_approved
    })
    await broadcaster.broadcast("notification", {"user_id": instance.user_id})

    return instance


# --- Reward Endpoints ---


@app.post("/rewards/", response_model=schemas.Reward)
def create_reward(reward: schemas.RewardCreate, db: Session = Depends(get_db)):
    return crud.create_reward(db=db, reward=reward)


@app.get("/rewards/", response_model=List[schemas.Reward])
def read_rewards(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rewards = crud.get_rewards(db, skip=skip, limit=limit)
    return rewards


@app.post("/users/{user_id}/goal", response_model=schemas.User)
def set_user_goal(user_id: int, reward_id: int, db: Session = Depends(get_db)):
    user = crud.set_user_goal(db, user_id=user_id, reward_id=reward_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/rewards/{reward_id}/redeem", response_model=schemas.RedemptionResponse)
async def redeem_reward(reward_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Redeem a reward for a user.
    Deducts points, creates a REDEEM transaction, and optionally clears goal.
    """
    logger.info(f"Redeeming reward {reward_id} for user {user_id}")
    result = crud.redeem_reward(db, user_id=user_id, reward_id=reward_id)

    if not result["success"]:
        logger.warning(f"Redemption failed: {result['error']}")
        raise HTTPException(status_code=400, detail=result["error"])

    logger.info(f"Redemption successful: {result['reward_name']} for {result['points_spent']} points")

    # Notify User
    crud.create_notification(db, schemas.NotificationCreate(
        user_id=user_id,
        type="REWARD_REDEEMED",
        title="Reward Redeemed!",
        message=f"You redeemed '{result['reward_name']}' for {result['points_spent']} points."
    ))

    # Broadcast SSE event for real-time updates
    await broadcaster.broadcast("reward_redeemed", {
        "user_id": user_id,
        "reward_id": reward_id,
        "reward_name": result["reward_name"],
        "points_spent": result["points_spent"],
        "remaining_points": result["remaining_points"]
    })
    await broadcaster.broadcast("notification", {"user_id": user_id})

    return result


@app.post("/rewards/{reward_id}/redeem-split", response_model=schemas.SplitRedemptionResponse)
async def redeem_reward_split(
    reward_id: int,
    request: schemas.SplitRedemptionRequest,
    db: Session = Depends(get_db)
):
    """
    Redeem a reward by pooling points from multiple users.
    Each contributing user gets their own transaction record.
    """
    logger.info(f"Split redemption for reward {reward_id} with {len(request.contributions)} contributors")

    # Convert contributions to list of dicts
    contributions = [{"user_id": c.user_id, "points": c.points} for c in request.contributions]

    result = crud.redeem_reward_split(db, reward_id=reward_id, contributions=contributions)

    if not result["success"]:
        logger.warning(f"Split redemption failed: {result['error']}")
        raise HTTPException(status_code=400, detail=result["error"])

    logger.info(f"Split redemption successful: {result['reward_name']} for {result['total_points']} points")

    # Broadcast SSE event for real-time updates
    await broadcaster.broadcast("reward_redeemed", {
        "reward_id": reward_id,
        "reward_name": result["reward_name"],
        "total_points": result["total_points"],
        "contributors": result["transactions"],
        "is_split": True
    })

    # Notify all contributors
    for tx in result["transactions"]:
        crud.create_notification(db, schemas.NotificationCreate(
            user_id=tx["user_id"],
            type="REWARD_REDEEMED",
            title="Group Reward Redeemed!",
            message=f"You contributed {tx['points']} points to '{result['reward_name']}'."
        ))
        await broadcaster.broadcast("notification", {"user_id": tx["user_id"]})

    return result


# --- Transaction Endpoints ---


@app.get("/users/{user_id}/transactions", response_model=List[schemas.Transaction])
def read_user_transactions(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    db: Session = Depends(get_db)
):
    """Get history for a specific user."""
    return crud.get_user_transactions(
        db, user_id=user_id, skip=skip, limit=limit,
        type=type, search=search, start_date=start_date, end_date=end_date
    )


@app.get("/transactions", response_model=List[schemas.Transaction])
def read_all_transactions(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    type: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    db: Session = Depends(get_db)
):
    """Get global history (for Admin/Family Dashboard)."""
    return crud.get_all_transactions(
        db, skip=skip, limit=limit,
        user_id=user_id, type=type, search=search, start_date=start_date, end_date=end_date
    )


# --- Settings Endpoints ---


@app.get("/settings/language/default", response_model=schemas.SystemSettings)
def get_default_language(db: Session = Depends(get_db)):
    setting = crud.get_system_setting(db, "default_language")
    if not setting:
        # Create default if not exists
        setting = crud.set_system_setting(db, "default_language", "en", "Family default language")
    return setting


@app.put("/settings/language/default", response_model=schemas.SystemSettings)
def set_default_language(setting: schemas.SystemSettingsBase, db: Session = Depends(get_db)):
    return crud.set_system_setting(db, "default_language", setting.value, setting.description)


@app.put("/users/{user_id}/language", response_model=schemas.User)
def update_user_language(user_id: int, lang_update: schemas.UserLanguageUpdate, db: Session = Depends(get_db)):
    user = crud.update_user_language(db, user_id=user_id, language=lang_update.preferred_language or "")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
