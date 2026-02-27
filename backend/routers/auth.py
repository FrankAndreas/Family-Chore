from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from .. import schemas, crud, security
from ..database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Auth"])


@router.post("/login/", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for user: {user_credentials.nickname}")
    user = crud.get_user_by_nickname(db, nickname=user_credentials.nickname)
    if not user:
        logger.warning(
            f"Login failed - user not found: {user_credentials.nickname}")
        raise HTTPException(status_code=404, detail="User not found")

    stored_pin = str(user.login_pin)
    is_bcrypt_hash = stored_pin.startswith("$2b$") or stored_pin.startswith("$2a$")

    if is_bcrypt_hash:
        # Standard bcrypt verification
        if not security.verify_password(user_credentials.login_pin, stored_pin):
            logger.warning(f"Login failed - incorrect PIN for user: {user_credentials.nickname}")
            raise HTTPException(status_code=401, detail="Incorrect PIN")
    else:
        # Legacy plaintext verification + Auto-migration
        logger.info(f"Unencrypted PIN detected for user: {user_credentials.nickname}. Checking legacy match...")
        if user_credentials.login_pin != stored_pin:
            logger.warning(f"Login failed - incorrect plaintext PIN for user: {user_credentials.nickname}")
            raise HTTPException(status_code=401, detail="Incorrect PIN")

        # Plaintext matched! Auto-migrate to bcrypt hash
        logger.info(f"Plaintext PIN matched. Auto-migrating PIN to bcrypt hash for user: {user_credentials.nickname}")
        new_hashed_pin = security.get_password_hash(user_credentials.login_pin)
        crud.update_user_pin(db, int(user.id), new_hashed_pin)

    logger.info(
        f"Login successful for user: {user_credentials.nickname} (ID: {user.id})")

    access_token = security.create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
