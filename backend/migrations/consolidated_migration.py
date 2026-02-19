import logging
from sqlalchemy import text
from backend.database import engine

logger = logging.getLogger(__name__)


def run_consolidated_migration(conn):
    """
    Consolidated migration for v1.1, v1.2, and v1.3.
    This function is idempotent and adds missing columns to existing tables.
    """
    logger.info("Running consolidated migration...")

    # 1. Tasks Table Updates
    task_columns = [
        ("requires_photo_verification", "TEXT DEFAULT 'false'"),
        ("recurrence_min_days", "INTEGER"),
        ("recurrence_max_days", "INTEGER")
    ]

    for col_name, col_type in task_columns:
        try:
            conn.execute(text(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_type}"))
            logger.info(f"✓ Added column tasks.{col_name}")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                logger.debug(f"ℹ column tasks.{col_name} already exists")
            else:
                logger.error(f"Error adding tasks.{col_name}: {e}")

    # 2. Transactions Table Updates
    try:
        conn.execute(text("ALTER TABLE transactions ADD COLUMN description TEXT"))
        logger.info("✓ Added column transactions.description")
    except Exception as e:
        if "duplicate column name" in str(e).lower():
            logger.debug("ℹ column transactions.description already exists")
        else:
            logger.error(f"Error adding transactions.description: {e}")

    # 3. Users Table Updates
    user_columns = [
        ("preferred_language", "TEXT"),
        ("current_streak", "INTEGER DEFAULT 0 NOT NULL"),
        ("last_task_date", "DATE")
    ]

    for col_name, col_type in user_columns:
        try:
            conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
            logger.info(f"✓ Added column users.{col_name}")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                logger.debug(f"ℹ column users.{col_name} already exists")
            else:
                logger.error(f"Error adding users.{col_name}: {e}")

    conn.commit()
    logger.info("Consolidated migration completed successfully.")


if __name__ == "__main__":
    # Manual execution support
    logging.basicConfig(level=logging.INFO)
    with engine.connect() as connection:
        run_consolidated_migration(connection)
