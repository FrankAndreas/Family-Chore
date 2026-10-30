from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import List
import logging

from .. import schemas, crud, hub, hub_people, models
from ..services import users as users_service, notifications
from ..database import get_db
from ..dependencies import (
    ADMIN_ROLE_NAME,
    TUNNEL_HEADER,
    get_current_admin_user,
    get_current_user,
    is_admin,
    request_token,
    require_self_or_admin,
)
from ..events import broadcaster
from ..notifications_service import send_push_to_user_background

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Users"])


@router.get("/hub")
def hub_link(request: Request):
    """Where browsers log in (the family hub's address at home) and out: at home the hub's logout page, which ends the
    login for every app; from outside Cloudflare Access's logout (spec 2026-10-30)."""
    outside = TUNNEL_HEADER in request.headers
    logout = "/cdn-cgi/access/logout" if outside else f"{hub.public_url()}/logout"
    return {"login_url": hub.public_url(), "logout_url": logout}


@router.get("/users/me", response_model=schemas.User)
def read_me(current_user: models.User = Depends(get_current_user)):
    """Who is logged in (the family hub's login)."""
    return current_user


def _ask_the_hub(request: Request, db: Session) -> None:
    """The people lists show the hub's current state, not the one of up to a minute ago."""
    token, _ = request_token(request)
    if token:
        try:
            hub_people.refresh(db, token, force=True)
        except hub.HubUnavailable:
            raise HTTPException(status_code=503, detail="hub_unavailable") from None


@router.get("/users/", response_model=List[schemas.UserPublic], dependencies=[Depends(get_current_user)])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)


@router.get("/users/admin", response_model=List[schemas.User], dependencies=[Depends(get_current_admin_user)])
def read_users_admin(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Admin-only: returns full user list including email addresses."""
    _ask_the_hub(request, db)
    return crud.get_users(db, skip=skip, limit=limit)


@router.get("/users/removed", response_model=List[schemas.User], dependencies=[Depends(get_current_admin_user)])
def read_removed_users(request: Request, db: Session = Depends(get_db)):
    """Admin-only: people the family hub no longer lists, hidden with their points until deleted here."""
    _ask_the_hub(request, db)
    return crud.get_removed_users(db)


@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: schemas.UserUpdate,
                current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update what only this app knows about a person: e-mail, notifications, and a child's game role. The name and
    whether someone is a parent (Admin) come from the family hub."""
    # Authorization: Only Admin or the user themselves can update their profile.
    require_self_or_admin(current_user, user_id)
    target = crud.get_user(db, user_id=user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user_update.nickname is not None and user_update.nickname != target.nickname:
        raise HTTPException(status_code=400, detail="name_from_hub")

    if user_update.role_id is not None and user_update.role_id != target.role_id:
        # Role updates are Admin-only, and only a child's game role: parents are Admin through the hub
        if not is_admin(current_user):
            raise HTTPException(status_code=403, detail="Only Admins can change roles")
        if is_admin(target):
            raise HTTPException(status_code=400, detail="role_from_hub")
        new_role = db.get(models.Role, user_update.role_id)
        if new_role is None:
            raise HTTPException(status_code=404, detail="Role not found")
        if new_role.name == ADMIN_ROLE_NAME:
            raise HTTPException(status_code=400, detail="admin_from_hub")

    user = crud.update_user(db, user_id=user_id, user_update=user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/users/{user_id}", dependencies=[Depends(get_current_admin_user)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Admin only: deletes the points and history of someone the family hub no longer lists."""
    target = crud.get_user(db, user_id=user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")
    # Only people the hub no longer lists: an active family member's data is never deleted by mistake
    if target.is_active:
        raise HTTPException(status_code=409, detail="still_in_hub")
    crud.delete_user(db, user_id=user_id)
    return {"success": True}


@router.post("/users/{user_id}/penalize",
             response_model=schemas.PenaltyResponse,
             dependencies=[Depends(get_current_admin_user)])
async def penalize_user(
    user_id: int,
    penalty: schemas.PenaltyRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Admin endpoint to deduct points from a user."""
    logger.info(
        f"Penalizing user {user_id} for {penalty.points} points: {penalty.reason}")
    result = users_service.apply_penalty(db, user_id=user_id, penalty=penalty)

    # Notify User in-app
    notifications.create_notification(db, schemas.NotificationCreate(
        user_id=user_id,
        type="SYSTEM",
        title="Points Deducted",
        message=f"You lost {result.points_deducted} points. Reason: {penalty.reason}"
    ))

    # Send Push Notification
    send_push_to_user_background(
        background_tasks,
        user_id,
        "Points Deducted",
        f"You lost {result.points_deducted} points. Reason: {penalty.reason}"
    )

    # Broadcast SSE events
    await broadcaster.broadcast("user_penalized", {
        "user_id": user_id,
        "points_deducted": result.points_deducted,
        "remaining_points": result.remaining_points,
        "reason": penalty.reason
    })
    await broadcaster.broadcast("notification", {"user_id": user_id})

    return result
