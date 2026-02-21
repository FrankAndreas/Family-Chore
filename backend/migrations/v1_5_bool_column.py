import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)


def run_v1_5_migration(conn):
    """
    Migration v1.5: Convert requires_photo_verification from TEXT to INTEGER.

    SQLite doesn't support ALTER COLUMN, so we:
    1. Add a new INTEGER column
    2. Copy data, converting 'true'/'1' -> 1, everything else -> 0
    3. Drop the old column
    4. Rename the new column

    This migration is idempotent.
    """
    logger.info(
        "Running v1.5 migration: requires_photo_verification TEXT -> INTEGER...")

    try:
        # Check if the column is still TEXT by inspecting table info
        result = conn.execute(text("PRAGMA table_info(tasks)"))
        columns = {row[1]: row[2] for row in result.fetchall()}

        if "requires_photo_verification" not in columns:
            logger.info(
                "Column requires_photo_verification doesn't exist yet, skipping conversion")
            conn.commit()
            return

        col_type = columns["requires_photo_verification"].upper()

        if col_type == "INTEGER":
            logger.info(
                "Column requires_photo_verification is already INTEGER, skipping")
            conn.commit()
            return

        # Column is still TEXT, convert it
        # Step 1: Add temporary INTEGER column
        conn.execute(text(
            "ALTER TABLE tasks ADD COLUMN requires_photo_verification_new INTEGER DEFAULT 0"
        ))

        # Step 2: Copy data with conversion
        conn.execute(text("""
            UPDATE tasks SET requires_photo_verification_new =
                CASE
                    WHEN LOWER(requires_photo_verification) IN ('true', '1') THEN 1
                    ELSE 0
                END
        """))

        # Step 3 & 4: SQLite doesn't support DROP COLUMN in older versions,
        # but Python 3.12 ships with SQLite 3.41+ which does support it.
        conn.execute(
            text("ALTER TABLE tasks DROP COLUMN requires_photo_verification"))
        conn.execute(text(
            "ALTER TABLE tasks RENAME COLUMN requires_photo_verification_new "
            "TO requires_photo_verification"
        ))

        conn.commit()
        logger.info(
            "✓ Converted requires_photo_verification from TEXT to INTEGER")

    except Exception as e:
        logger.error(f"v1.5 migration error: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from backend.database import engine
    with engine.connect() as connection:
        run_v1_5_migration(connection)
