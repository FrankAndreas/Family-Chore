from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from .. import schemas, crud
from ..database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Auth"])


@router.post("/login/", response_model=schemas.User)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for user: {user_credentials.nickname}")
    user = crud.get_user_by_nickname(db, nickname=user_credentials.nickname)
    if not user:
        logger.warning(
            f"Login failed - user not found: {user_credentials.nickname}")
        raise HTTPException(status_code=404, detail="User not found")
    if user.login_pin != user_credentials.login_pin:
        logger.warning(
            f"Login failed - incorrect PIN for user: {user_credentials.nickname}")
        raise HTTPException(status_code=401, detail="Incorrect PIN")
    logger.info(
        f"Login successful for user: {user_credentials.nickname} (ID: {user.id})")
    return user
