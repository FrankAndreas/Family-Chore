import datetime
from datetime import timezone
import logging

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, crud
from ..database import get_db
from ..dependencies import get_current_user, get_current_admin_user
from ..notifications_service import send_email_background
from ..events import broadcaster

logger = logging.getLogger(__name__)

router = APIRouter(tags=["System"])


@router.get("/tasks/export", response_model=schemas.TasksExport, dependencies=[Depends(get_current_admin_user)])
def export_tasks(db: Session = Depends(get_db)):
    """Export all tasks in a human-readable format for backup or AI generation."""
    logger.info("Exporting all tasks...")
    tasks = crud.get_tasks(db)

    # Build role name lookup
    roles = {r.id: r.name for r in crud.get_roles(db)}

    export_items = []
    for task in tasks:
        export_items.append(schemas.TaskExportItem(
            name=str(task.name),
            description=str(task.description) if task.description else "",
            base_points=int(str(task.base_points)),
            assigned_role=str(roles.get(task.assigned_role_id))
            if task.assigned_role_id and roles.get(task.assigned_role_id) else None,
            schedule_type=str(task.schedule_type),
            default_due_time=str(task.default_due_time) if task.default_due_time else "",
            recurrence_min_days=int(str(task.recurrence_min_days)) if task.recurrence_min_days is not None else None,
            recurrence_max_days=int(str(task.recurrence_max_days)) if task.recurrence_max_days is not None else None,
            requires_photo_verification=bool(task.requires_photo_verification),
        ))

    logger.info(f"Exported {len(export_items)} tasks")
    return schemas.TasksExport(
        version="1.0",
        exported_at=datetime.datetime.now(timezone.utc).isoformat(),
        tasks=export_items
    )


@router.post("/tasks/import", dependencies=[Depends(get_current_admin_user)])
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
        # Map Parent/Elternteil to Admin or specific role if exists? Seed data has Admin.
        "elternteil": "admin",
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
                    errors.append(
                        f"Task '{task_item.name}': Unknown role '{task_item.assigned_role}'")
                    continue
                assigned_role_id = roles[role_name_lower]

            # Create the task using existing schema
            task_create = schemas.TaskCreate(
                name=task_item.name,
                description=task_item.description,
                base_points=task_item.base_points,
                assigned_role_id=int(assigned_role_id) if assigned_role_id else None,
                schedule_type=task_item.schedule_type,
                default_due_time=task_item.default_due_time,
                recurrence_min_days=task_item.recurrence_min_days,
                recurrence_max_days=task_item.recurrence_max_days,
                requires_photo_verification=task_item.requires_photo_verification,
            )
            new_task = crud.create_task(db=db, task=task_create)
            created.append(new_task.name)
            # Prevent duplicates within import
            existing_names.add(task_item.name.lower())
            logger.info(f"Imported task: {new_task.name} (ID: {new_task.id})")

        except Exception as e:
            errors.append(f"Task '{task_item.name}': {str(e)}")

    # Broadcast SSE event if any tasks were created
    if created:
        await broadcaster.broadcast("tasks_imported", {"count": len(created)})

    logger.info(
        f"Import complete: {len(created)} created, {len(skipped)} skipped, {len(errors)} errors")

    return {
        "success": len(errors) == 0,
        "created": created,
        "skipped": skipped,
        "errors": errors,
        "summary": f"Created {len(created)} tasks, skipped {len(skipped)}, {len(errors)} errors"
    }


@router.post("/daily-reset/", dependencies=[Depends(get_current_admin_user)])
def trigger_daily_reset(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    logger.info("Triggering daily reset...")
    count = crud.generate_daily_instances(db)

    # Send daily reminders via Email
    users_to_notify = crud.get_users_with_pending_daily_tasks(db)
    notified_count = 0
    for user in users_to_notify:
        if user.email:
            send_email_background(
                background_tasks,
                to_email=str(user.email),
                subject="Your Daily Chores Await!",
                body=f"Hi {user.nickname},\n\nYou have uncompleted daily chores waiting for you. Let's get them done!"
            )
            notified_count += 1

    logger.info(
        f"Daily reset complete. Created {count} task instances. Queued {notified_count} emails.")
    return {"message": f"Daily reset complete. Created {count} task instances. Queued {notified_count} emails."}


@router.get("/settings/language/default",
            response_model=schemas.SystemSettings,
            dependencies=[Depends(get_current_user)])
def get_default_language(db: Session = Depends(get_db)):
    setting = crud.get_system_setting(db, "default_language")
    if not setting:
        # Create default if not exists
        setting = crud.set_system_setting(
            db, "default_language", "en", "Family default language")
    return setting


@router.put("/settings/language/default",
            response_model=schemas.SystemSettings,
            dependencies=[Depends(get_current_admin_user)])
def set_default_language(setting: schemas.SystemSettingsBase, db: Session = Depends(get_db)):
    return crud.set_system_setting(db, "default_language", setting.value, setting.description)


@router.put("/users/{user_id}/language", response_model=schemas.User, dependencies=[Depends(get_current_user)])
def update_user_language(user_id: int, lang_update: schemas.UserLanguageUpdate, db: Session = Depends(get_db)):
    user = crud.update_user_language(
        db, user_id=user_id, language=lang_update.preferred_language or "")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
