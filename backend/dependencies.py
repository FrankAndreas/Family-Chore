"""Who is logged in: the family hub's login (spec 2026-10-30), as in the budget app and the meal planner.

At home the browser sends the hub's cookie `hub_session` (set for local.<domain>, so every family app gets it); tests
and scripts may send the same token as `Authorization: Bearer`. The hub says whose login it is and whether they may
use the chores app; the app's people come from the hub too (hub_people.py). No PINs here any more."""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from . import hub, hub_people, models
from .database import get_db

logger = logging.getLogger(__name__)

COOKIE = "hub_session"
# With the cookie, a change must carry this header: another site can make the browser send the cookie (sibling apps
# share the site), but not a custom header without this app allowing it
CSRF_HEADER = "X-Requested-With"
CSRF_VALUE = "chores"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
TUNNEL_HEADER = "Cf-Connecting-Ip"
ADMIN_ROLE_NAME = "Admin"


def request_token(request: Request) -> tuple[Optional[str], bool]:
    """The hub token of the request, and whether it came as the cookie."""
    scheme, _, value = request.headers.get("Authorization", "").partition(" ")
    if scheme.lower() == "bearer" and value.strip():
        return value.strip(), False
    cookie = request.cookies.get(COOKIE)
    return (cookie, True) if cookie else (None, False)


def _not_logged_in() -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, "not_logged_in", headers={"WWW-Authenticate": "Bearer"})


def _active(db: Session, hub_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.hub_id == hub_id, models.User.is_active.is_(True)).first()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    """The person behind the request's login. A plain function: FastAPI runs it in a worker thread (the hub)."""
    # Home only: Cloudflare sets this on everything through its tunnel; a hub login arriving from outside can only be a
    # stolen home cookie (family-hub README, "For apps")
    if TUNNEL_HEADER in request.headers:
        raise _not_logged_in()
    token, from_cookie = request_token(request)
    if not token:
        raise _not_logged_in()
    if from_cookie and request.method not in SAFE_METHODS and request.headers.get(CSRF_HEADER) != CSRF_VALUE:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "csrf")
    try:
        person, access = hub.session(token)
        if person is None:
            raise _not_logged_in()
        if not access:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "no_access")
        hub_people.refresh(db, token)
        user = _active(db, person.id)
        if user is None:
            # Given access a moment ago: the people kept here are older than that
            hub_people.refresh(db, token, force=True)
            user = _active(db, person.id)
        elif is_admin(user) != (person.role == "PARENT"):
            # The hub's role is newer than the row's (refreshed once a minute)
            hub_people.refresh(db, token, force=True)
            db.refresh(user)
    except hub.HubUnavailable as error:
        logger.warning("The family hub can't be reached (%s)", error)
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "hub_unavailable") from None
    if user is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "no_access")
    return user


def is_admin(user) -> bool:
    return bool(user.role and user.role.name == ADMIN_ROLE_NAME)


def require_self_or_admin(current_user, user_id: int) -> None:
    if current_user.id != user_id and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )


def get_current_admin_user(current_user=Depends(get_current_user)):
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
