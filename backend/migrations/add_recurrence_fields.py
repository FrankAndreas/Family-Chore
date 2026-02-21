"""Add recurrence fields to tasks table

This migration adds support for recurring tasks with cooldown periods.

To apply this migration:
1. Stop the backend server
2. Run: PYTHONPATH=/home/andreas/work/family-chore ./venv/bin/python backend/migrations/add_recurrence_fields.py
3. Restart the backend server
"""

from sqlalchemy import text
from backend.database import engine


def add_recurrence_fields():
    """Add recurrence_min_days and recurrence_max_days columns to tasks table."""

    # Use raw SQL to add columns
    with engine.connect() as conn:
        try:
            # Add recurrence_min_days column
            conn.execute(
                text("ALTER TABLE tasks ADD COLUMN recurrence_min_days INTEGER"))
            print("✓ Added recurrence_min_days column")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ recurrence_min_days column already exists")
            else:
                raise

        try:
            # Add recurrence_max_days column
            conn.execute(
                text("ALTER TABLE tasks ADD COLUMN recurrence_max_days INTEGER"))
            print("✓ Added recurrence_max_days column")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ recurrence_max_days column already exists")
            else:
                raise

        conn.commit()

    print("\n✅ Migration completed successfully!")
    print("You can now create recurring tasks with cooldown periods.")


if __name__ == "__main__":
    add_recurrence_fields()
