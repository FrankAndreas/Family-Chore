from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import logging
import asyncio
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from . import models, schemas, crud
from .database import SessionLocal, engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="ChoreSpec MVP")


# SSE: Event broadcasting system
class EventBroadcaster:
    def __init__(self):
        self.clients: List[asyncio.Queue] = []

    async def subscribe(self) -> asyncio.Queue:
        queue = asyncio.Queue()
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


@app.on_event("startup")
def on_startup():
    # Ensure tables exist
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

    # Start the midnight scheduler
    scheduler.add_job(
        scheduled_daily_reset,
        trigger=CronTrigger(hour=0, minute=0),  # Run at midnight
        id="daily_reset_job",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Midnight scheduler started - daily reset will run at 00:00")


@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown()
    logger.info("Scheduler shut down")


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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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

    return {"message": f"Role deleted successfully. {len(users_with_role)} users reassigned, {len(tasks_with_role)} tasks updated."}

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
    instance = crud.complete_task_instance(db, instance_id=instance_id, actual_user_id=actual_user_id)
    if not instance:
        logger.error(f"Task instance not found: {instance_id}")
        raise HTTPException(status_code=404, detail="Task instance not found")
    logger.info(f"Task completed successfully: instance {instance_id} by user {instance.user_id}")

    # Broadcast SSE event for real-time updates
    await broadcaster.broadcast("task_completed", {"instance_id": instance_id, "user_id": instance.user_id})

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
    user = crud.update_user_language(db, user_id=user_id, language=lang_update.preferred_language)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
