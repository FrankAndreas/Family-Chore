import logging
from backend.database import engine, SessionLocal
from backend.crud import get_system_setting, set_system_setting
from backend.migrations.consolidated_migration import run_consolidated_migration

logger = logging.getLogger(__name__)

CURRENT_TARGET_VERSION = "1.3"


class MigrationManager:
    @staticmethod
    def get_current_db_version(db) -> str:
        try:
            setting = get_system_setting(db, "db_version")
            if setting:
                return str(setting.value)
        except Exception:
            # Table might not exist yet if it's a fresh DB
            return "1.0"
        return "1.0"  # Assume 1.0 if not set

    @staticmethod
    def run_migrations():
        """
        Check database version and run migrations if needed.
        Called on backend startup.
        """
        db = SessionLocal()
        try:
            current_version = MigrationManager.get_current_db_version(db)
            logger.info(f"Database version check: current={current_version}, target={CURRENT_TARGET_VERSION}")

            if current_version < CURRENT_TARGET_VERSION:
                logger.info(f"Database outdated. Starting migration to {CURRENT_TARGET_VERSION}...")

                with engine.connect() as conn:
                    # Run the consolidated migration
                    run_consolidated_migration(conn)

                    # Update the version in system_settings
                    set_system_setting(
                        db, "db_version", CURRENT_TARGET_VERSION, f"Schema version {CURRENT_TARGET_VERSION}"
                    )

                logger.info(f"Database successfully migrated to {CURRENT_TARGET_VERSION}")
            else:
                logger.info("Database version is up to date.")

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            # We don't raise here to allow backend to attempt to start anyway,
            # but main.py should be aware of this risk.
        finally:
            db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    MigrationManager.run_migrations()
