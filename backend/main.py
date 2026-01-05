from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import logging

from . import models, schemas, crud
from .database import SessionLocal, engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="ChoreSpec MVP")


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


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative React dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get("/roles/", response_model=List[schemas.Role])
def read_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    roles = crud.get_roles(db, skip=skip, limit=limit)
    return roles


@app.put("/roles/{role_id}", response_model=schemas.Role)
def update_role(role_id: int, role_update: schemas.RoleUpdate, db: Session = Depends(get_db)):
    db_role = crud.get_role(db, role_id=role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Validation (AC 2.4)
    if role_update.multiplier_value < 0.1:
        raise HTTPException(status_code=400, detail="Multiplier must be >= 0.1")

    return crud.update_role_multiplier(db, role_id=role_id, multiplier=role_update.multiplier_value)

# --- Task Endpoints ---


@app.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating task: {task.name} with {task.base_points} base points")
    created_task = crud.create_task(db=db, task=task)
    logger.info(f"Task created successfully: {created_task.name} (ID: {created_task.id})")
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


@app.post("/daily-reset/")
def trigger_daily_reset(db: Session = Depends(get_db)):
    logger.info("Triggering daily reset...")
    count = crud.generate_daily_instances(db)
    logger.info(f"Daily reset complete. Created {count} task instances.")
    return {"message": f"Daily reset complete. Created {count} task instances."}


@app.get("/tasks/daily/{user_id}", response_model=List[schemas.TaskInstance])
def read_user_daily_tasks(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_daily_tasks(db, user_id=user_id)


@app.post("/tasks/{instance_id}/complete", response_model=schemas.TaskInstance)
def complete_task(instance_id: int, db: Session = Depends(get_db)):
    logger.info(f"Attempting to complete task instance: {instance_id}")
    instance = crud.complete_task_instance(db, instance_id=instance_id)
    if not instance:
        logger.error(f"Task instance not found: {instance_id}")
        raise HTTPException(status_code=404, detail="Task instance not found")
    logger.info(f"Task completed successfully: instance {instance_id} by user {instance.user_id}")
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
