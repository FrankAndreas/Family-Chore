import os
from passlib.context import CryptContext
from typing import cast, Optional, Dict, Any
import jwt
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_DEFAULT_SECRET = "dev-only-secret-CHANGE-ME-in-production"
SECRET_KEY = os.getenv("JWT_SECRET_KEY", _DEFAULT_SECRET)
if SECRET_KEY == _DEFAULT_SECRET:
    logger.warning("JWT_SECRET_KEY not set! Using insecure default. Set JWT_SECRET_KEY env var in production.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


def get_password_hash(password: str) -> str:
    """Hash a password/PIN using bcrypt."""
    return cast(str, pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password/PIN against its hashed version."""
    return cast(bool, pwd_context.verify(plain_password, hashed_password))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a JWT token and return its payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        logger.error(f"JWT Verification Error: {e}")
        return None
