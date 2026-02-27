from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from .. import schemas, crud, models
from ..database import get_db
from ..dependencies import get_current_user, get_current_admin_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Roles"])


@router.post("/roles/", response_model=schemas.Role, dependencies=[Depends(get_current_admin_user)])
def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    """Create a new role."""
    logger.info(
        f"Creating role: {role.name} with multiplier {role.multiplier_value}")
    # Check if role name already exists
    existing = db.query(models.Role).filter(
        models.Role.name == role.name).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Role with this name already exists")

    if role.multiplier_value < 0.1:
        raise HTTPException(
            status_code=400, detail="Multiplier must be >= 0.1")

    db_role = models.Role(
        name=role.name, multiplier_value=role.multiplier_value)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    logger.info(f"Role created: {db_role.name} (ID: {db_role.id})")
    return db_role


@router.get("/roles/", response_model=List[schemas.Role], dependencies=[Depends(get_current_user)])
def read_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    roles = crud.get_roles(db, skip=skip, limit=limit)
    return roles


@router.get("/roles/{role_id}/users", dependencies=[Depends(get_current_user)])
def get_role_users(role_id: int, db: Session = Depends(get_db)):
    """Get count of users assigned to a role."""
    users = db.query(models.User).filter(models.User.role_id == role_id).all()
    return {"count": len(users), "users": [{"id": u.id, "nickname": u.nickname} for u in users]}


@router.put("/roles/{role_id}", response_model=schemas.Role, dependencies=[Depends(get_current_admin_user)])
def update_role(role_id: int, role_update: schemas.RoleUpdate, db: Session = Depends(get_db)):
    db_role = crud.get_role(db, role_id=role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Validation (AC 2.4)
    if role_update.multiplier_value < 0.1:
        raise HTTPException(
            status_code=400, detail="Multiplier must be >= 0.1")

    return crud.update_role_multiplier(db, role_id=role_id, multiplier=role_update.multiplier_value)


@router.delete("/roles/{role_id}", dependencies=[Depends(get_current_admin_user)])
def delete_role(role_id: int, reassign_to_role_id: int = None, db: Session = Depends(get_db)):
    """Delete a role. If users are assigned, reassign_to_role_id must be provided."""
    logger.info(
        f"Deleting role: {role_id}, reassign to: {reassign_to_role_id}")

    db_role = crud.get_role(db, role_id=role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Check if users are assigned to this role
    users_with_role = db.query(models.User).filter(
        models.User.role_id == role_id).all()

    if users_with_role:
        if not reassign_to_role_id:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete role: {len(users_with_role)} users are assigned. Provide reassign_to_role_id."
            )

        # Validate target role exists
        target_role = crud.get_role(db, role_id=reassign_to_role_id)
        if not target_role:
            raise HTTPException(
                status_code=400, detail="Target role for reassignment not found")

        # Reassign all users
        for user in users_with_role:
            user.role_id = reassign_to_role_id
        db.commit()
        logger.info(
            f"Reassigned {len(users_with_role)} users from role {role_id} to {reassign_to_role_id}")

    # Also update tasks assigned to this role
    tasks_with_role = db.query(models.Task).filter(
        models.Task.assigned_role_id == role_id).all()
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
