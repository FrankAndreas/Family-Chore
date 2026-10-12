import os
import secrets
from pathlib import Path
import bcrypt
from typing import cast, Optional, Dict, Any
import jwt
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

_BACKEND_DIR = Path(__file__).resolve().parent
_ENV_PATH = _BACKEND_DIR / ".env"


def _load_jwt_secret() -> str:
    """Load JWT secret from env, or auto-generate and persist if missing."""
    secret = os.getenv("JWT_SECRET_KEY", "")
    if secret:
        return secret

    # Auto-generate a cryptographically secure secret
    secret = secrets.token_hex(32)  # 64-char hex string (256 bits)
    logger.warning(
        "JWT_SECRET_KEY not set — auto-generated a new secret key. "
        "Set JWT_SECRET_KEY env var for production."
    )

    # Persist to .env so the key survives restarts
    env_lines = []
    if _ENV_PATH.exists():
        env_lines = _ENV_PATH.read_text().splitlines()

    # Remove old JWT_SECRET_KEY entry if present
    env_lines = [ln for ln in env_lines if not ln.startswith("JWT_SECRET_KEY=")]
    env_lines.append(f"JWT_SECRET_KEY={secret}")
    _ENV_PATH.write_text("\n".join(env_lines) + "\n")
    logger.info("JWT_SECRET_KEY written to .env")

    return secret


SECRET_KEY = _load_jwt_secret()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7
SSE_TOKEN_EXPIRE_MINUTES = 60  # short-lived token for SSE query-string use


def get_password_hash(password: str) -> str:
    """Hash a password/PIN using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password/PIN against its hashed version."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        # Malformed hash, or input longer than bcrypt's 72-byte limit
        return False


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


def create_sse_token(user_id: int) -> str:
    """Create a short-lived (1-hour) token for the SSE query-string."""
    return create_access_token(
        data={"sub": str(user_id), "sse": True},
        expires_delta=timedelta(minutes=SSE_TOKEN_EXPIRE_MINUTES),
    )


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a JWT token and return its payload."""
    try:
        payload = cast(Dict[str, Any], jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]))
        return payload
    except jwt.PyJWTError as e:
        logger.error(f"JWT Verification Error: {e}")
        return None
