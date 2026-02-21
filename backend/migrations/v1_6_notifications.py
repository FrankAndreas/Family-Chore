import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)


def run_v1_6_migration(conn):
    """
    Migration to V1.6
    Adds email and notifications_enabled columns to the users table.
    """
    try:
        # Check if the email column already exists
        result = conn.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result.fetchall()]

        if "email" not in columns:
            logger.info("Migrating to V1.6: Adding email column to users")
            conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR"))

        if "notifications_enabled" not in columns:
            logger.info(
                "Migrating to V1.6: Adding notifications_enabled column to users")
            conn.execute(
                text("ALTER TABLE users ADD COLUMN notifications_enabled INTEGER DEFAULT 1"))

    except Exception as e:
        logger.error(f"Failed to run V1.6 migration: {e}")
        raise
