import shutil
import os
import glob
import logging
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)


class BackupManager:
    """Manages database backups."""

    def __init__(self, db_path: str = "chorespec_mvp.db", backup_dir: str = "backups"):
        self.db_path = db_path
        self.backup_dir = backup_dir

        # Ensure backup directory exists
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def create_backup(self) -> str:
        """Creates a timestamped backup of the database."""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"chorespec_mvp_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_filename)

        try:
            shutil.copy2(self.db_path, backup_path)
            return backup_path
        except Exception as e:
            raise Exception(f"Failed to create backup: {str(e)}")

    def cleanup_old_backups(self, retention_days: int = 7) -> List[str]:
        """Deletes backups older than retention_days. Returns list of deleted files."""
        deleted_files = []
        pattern = os.path.join(self.backup_dir, "chorespec_mvp_*.db")
        backup_files = glob.glob(pattern)

        now = datetime.now()

        for file_path in backup_files:
            try:
                # Get file modification time
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                age_days = (now - file_time).days

                if age_days > retention_days:
                    os.remove(file_path)
                    deleted_files.append(file_path)
            except Exception as e:
                logger.error(f"Error checking/deleting backup {file_path}: {e}")

        return deleted_files

    def list_backups(self) -> List[Dict[str, object]]:
        """Returns a list of existing backups."""
        pattern = os.path.join(self.backup_dir, "chorespec_mvp_*.db")
        backup_files = glob.glob(pattern)

        backups: List[Dict[str, object]] = []
        for file_path in backup_files:
            try:
                timestamp = os.path.getmtime(file_path)
                size = os.path.getsize(file_path)
                backups.append({
                    "filename": os.path.basename(file_path),
                    "created_at": datetime.fromtimestamp(timestamp).isoformat(),
                    "size_bytes": size
                })
            except Exception:
                continue

        # Sort by creation time descending
        backups.sort(key=lambda x: str(x["created_at"]), reverse=True)
        return backups
