import logging
from sqlalchemy import text
from backend.security import get_password_hash

logger = logging.getLogger(__name__)


def run_v1_8_migration(conn):
    """
    Migration to hash existing plaintext PINs.
    Version: 1.8
    """
    logger.info("Running v1.8 migration (Hash existing PINs)...")

    # Check if the users table exists (in case of new DB)
    table_check = conn.execute(text(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
    )).fetchone()

    if not table_check:
        logger.info("Users table not found, skipping PIN hashing migration.")
        return

    # Fetch all users
    users = conn.execute(text("SELECT id, login_pin FROM users")).fetchall()

    migrated_count = 0
    for user_id, pin in users:
        # A bcrypt hash starts with $2b$ or $2a$ and is typically 60 chars long.
        # If the PIN is already a dict-like or looks like a hash, skip it.
        # Plain text PINs in this system are exactly 4 digits.
        if pin and len(pin) == 4 and pin.isdigit():
            hashed_pin = get_password_hash(pin)
            conn.execute(
                text("UPDATE users SET login_pin = :hashed_pin WHERE id = :id"),
                {"hashed_pin": hashed_pin, "id": user_id}
            )
            migrated_count += 1

    if migrated_count > 0:
        logger.info(f"Successfully hashed PINs for {migrated_count} users.")
    else:
        logger.info("No plaintext PINs found to migrate.")

    logger.info("Completed v1.8 migration.")
