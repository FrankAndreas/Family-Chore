from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from contextlib import asynccontextmanager
import logging
import asyncio
import json
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from sqlalchemy import inspect
from alembic.config import Config
from alembic import command as alembic_command

from . import models, crud
from .database import engine, SessionLocal
from .routers import analytics, notifications, auth, users, roles, tasks, rewards, transactions, system
from .backup import BackupManager
from .notifications_service import send_email_sync, send_push_to_user_sync
from .dependencies import get_current_admin_user, get_current_user
from .security import verify_token
from .events import broadcaster


# Initialize Tables
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Background scheduler for midnight reset
scheduler = BackgroundScheduler()


def scheduled_daily_reset():
    """Scheduled job that runs at midnight to generate daily task instances."""
    logger.info("Midnight scheduler: Running daily reset...")
    db = SessionLocal()
    try:
        count = crud.perform_daily_reset_if_needed(db)
        if count > 0:
            logger.info(
                f"Midnight scheduler: Generated {count} task instances")
            # Send reminder emails directly (scheduler runs in its own thread)
            users_to_notify = crud.get_users_with_pending_daily_tasks(db)
            notified_count = 0
            for user in users_to_notify:
                # Always attempt to send a push notification
                try:
                    send_push_to_user_sync(
                        user.id,
                        "Your Daily Chores Await!",
                        f"Hi {user.nickname}, you have uncompleted daily chores waiting for you."
                    )
                except Exception as push_err:
                    logger.error(f"Midnight scheduler: Failed to send push to {user.nickname}: {push_err}")

                if user.email:
                    try:
                        send_email_sync(
                            str(user.email),
                            "Your Daily Chores Await!",
                            f"Hi {user.nickname},\n\n"
                            "You have uncompleted daily chores waiting for you. Let's get them done!"
                        )
                        notified_count += 1
                    except Exception as email_err:
                        logger.error(
                            f"Midnight scheduler: Failed to send email to {user.nickname}: {email_err}"
                        )

            if notified_count > 0:
                logger.info(
                    f"Midnight scheduler: Sent {notified_count} reminder emails.")

        else:
            logger.info("Midnight scheduler: No new instances needed")
    except Exception as e:
        logger.error(f"Midnight scheduler failed: {e}")
    finally:
        db.close()


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
    # 1. Run migrations first to ensure schema is up-to-date (unless running tests)
    if os.getenv("TESTING") != "True":
        alembic_cfg = Config("backend/alembic.ini")

        # Check if we need to stamp (backwards compatibility for existing SQLite)
        inspector = inspect(engine)
        if inspector.has_table("users") and not inspector.has_table("alembic_version"):
            logger.info("Existing database detected without Alembic tracking. Stamping to 'head'.")
            alembic_command.stamp(alembic_cfg, "head")

        logger.info("Running Alembic upgrade to 'head'.")
        alembic_command.upgrade(alembic_cfg, "head")

    # 2. Ensure tables exist (will create new tables if any)
    models.Base.metadata.create_all(bind=engine)
    # Seed initial data
    try:
        from .seed_data import seed_data
        seed_data()
    except Exception as e:
        logger.error(f"Failed to seed data: {e}")

    # Smart daily reset: Only generate if not already done today
    db = SessionLocal()
    try:
        count = crud.perform_daily_reset_if_needed(db)
        if count > 0:
            logger.info(f"Startup: Generated {count} task instances for today")
        else:
            logger.info(
                "Startup: Daily reset already performed today, skipping")
    except Exception as e:
        logger.error(f"Failed to generate daily instances on startup: {e}")
    finally:
        db.close()

    # Fetch system timezone (default to Europe/Berlin)
    timezone_str = "Europe/Berlin"
    db = SessionLocal()
    try:
        setting = crud.get_system_setting(db, "default_timezone")
        if setting:
            timezone_str = setting.value
        else:
            # Create default if not exists
            crud.set_system_setting(
                db, "default_timezone", timezone_str, "System-wide timezone for scheduler")
    except Exception as e:
        logger.error(f"Failed to fetch timezone setting: {e}")
    finally:
        db.close()

    logger.info(f"Configuring scheduler with timezone: {timezone_str}")
    scheduler.configure(timezone=timezone_str)

    # Start the midnight scheduler
    scheduler.add_job(
        scheduled_daily_reset,
        # Run at midnight local time
        trigger=CronTrigger(hour=0, minute=0, timezone=timezone_str),
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
    logger.info(
        "Midnight scheduler started - daily reset will run at 00:00, backups at 02:00")

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

# M1: Retrieve CORS internal network origins from environment or default to local Vite/React servers
cors_origins_env = os.environ.get("CORS_ORIGINS", "")
if cors_origins_env:
    allow_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
else:
    allow_origins = [
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",  # Vite dev server via IP
        "http://localhost:5174",  # Vite dev server (alt)
        "http://localhost:3000",  # Alternative React dev server
    ]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)


@app.get("/uploads/{filename}", tags=["System"])
def get_uploaded_file(filename: str, current_user: models.User = Depends(get_current_user)):
    """Serve uploaded files only to authenticated users."""
    file_path = os.path.join("uploads", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


# Include Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(tasks.router)
app.include_router(rewards.router)
app.include_router(transactions.router)
app.include_router(system.router)
app.include_router(analytics.router)
app.include_router(notifications.router)


@app.post("/backups/run", tags=["System"], dependencies=[Depends(get_current_admin_user)])
def trigger_manual_backup():
    """Manually trigger a backup in the background."""
    run_backup_job()
    return {"status": "Backup completed"}


# --- SSE Endpoint ---
@app.get("/events", tags=["System"])
async def sse_events(token: str = ""):
    """Server-Sent Events endpoint for real-time updates.

    Accepts JWT via ?token= query param because the native EventSource API
    cannot send Authorization headers.

    NOTE: Passing JWT in query strings means tokens may appear in server access
    logs, browser history, and proxy logs. Sanitise production logs accordingly.
    """
    if not token:
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})

    payload = verify_token(token)
    if payload is None:
        return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

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


@app.get("/", tags=["System"])
def read_root():
    return {"message": "Welcome to ChoreSpec API"}
