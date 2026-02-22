import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

# Maps table name -> list of (column_name, default_value_int)
BOOL_COLUMNS = {
    "users": [("notifications_enabled", 1)],
    "notifications": [("read", 0)],
    # requires_photo_verification was already converted TEXT->INTEGER in v1.5;
    # it is already stored as 0/1 INTEGER, which matches Boolean in SQLite.
    # No migration needed for that column — SQLAlchemy's Boolean maps to INTEGER on SQLite.
}


def run_v1_7_migration(conn) -> None:
    """
    Migration v1.7: Ensure boolean-ish columns are stored as INTEGER 0/1.

    On SQLite, `Boolean` is represented as INTEGER anyway, so this migration
    is primarily a *validation* step — it confirms each column exists and is
    INTEGER.  If a column were still TEXT (shouldn't happen for these), it
    would be converted using the same rename-swap approach from v1.5.

    The real change is in models.py (Column(Boolean)) and schemas.py (bool types).
    """
    logger.info("Running v1.7 migration: Boolean column validation...")

    try:
        for table, columns in BOOL_COLUMNS.items():
            result = conn.execute(text(f"PRAGMA table_info({table})"))
            col_info = {row[1]: row[2] for row in result.fetchall()}

            for col_name, default_val in columns:
                if col_name not in col_info:
                    logger.warning(
                        f"Column {table}.{col_name} not found — skipping")
                    continue

                col_type = col_info[col_name].upper()
                if col_type == "INTEGER":
                    logger.info(
                        f"✓ {table}.{col_name} is already INTEGER — no conversion needed")
                    continue

                # Convert TEXT -> INTEGER using rename-swap
                logger.info(
                    f"Converting {table}.{col_name} from {col_type} to INTEGER...")

                tmp_col = f"{col_name}_new"
                conn.execute(text(
                    f"ALTER TABLE {table} ADD COLUMN {tmp_col} INTEGER DEFAULT {default_val}"
                ))
                conn.execute(text(f"""
                    UPDATE {table} SET {tmp_col} =
                        CASE
                            WHEN LOWER({col_name}) IN ('true', '1') THEN 1
                            ELSE 0
                        END
                """))
                conn.execute(text(
                    f"ALTER TABLE {table} DROP COLUMN {col_name}"))
                conn.execute(text(
                    f"ALTER TABLE {table} RENAME COLUMN {tmp_col} TO {col_name}"))
                logger.info(
                    f"✓ Converted {table}.{col_name} from {col_type} to INTEGER")

        conn.commit()
        logger.info("v1.7 migration complete.")

    except Exception as e:
        logger.error(f"v1.7 migration error: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from backend.database import engine
    with engine.connect() as connection:
        run_v1_7_migration(connection)
