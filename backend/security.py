from passlib.context import CryptContext
from typing import cast

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password/PIN using bcrypt."""
    return cast(str, pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password/PIN against its hashed version."""
    return cast(bool, pwd_context.verify(plain_password, hashed_password))
