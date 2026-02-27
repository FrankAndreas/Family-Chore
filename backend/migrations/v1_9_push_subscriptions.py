import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)


def run_v1_9_migration(conn):
    """
    Migration to V1.9
    Adds push_subscriptions table for Web Push Notifications.
    """
    try:
        # Check if table exists
        result = conn.execute(text(
            "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='push_subscriptions'"
        ))
        if result.fetchone()[0] == 0:
            logger.info("Migrating to V1.9: Creating push_subscriptions table")
            conn.execute(text("""
                CREATE TABLE push_subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    endpoint VARCHAR UNIQUE NOT NULL,
                    p256dh VARCHAR NOT NULL,
                    auth VARCHAR NOT NULL,
                    created_at DATETIME NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """))
            conn.execute(text("""
                CREATE INDEX ix_push_subscriptions_user_id ON push_subscriptions(user_id)
            """))
            conn.execute(text("""
                CREATE INDEX ix_push_subscriptions_id ON push_subscriptions(id)
            """))
    except Exception as e:
        logger.error(f"Failed to run V1.9 migration: {e}")
        raise
