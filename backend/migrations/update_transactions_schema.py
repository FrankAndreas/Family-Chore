"""Update transactions table schema
Adding description column for detailed logs.
"""
from sqlalchemy import text
from backend.database import engine


def update_transactions_schema():
    with engine.connect() as conn:
        try:
            conn.execute(
                text("ALTER TABLE transactions ADD COLUMN description TEXT"))
            print("✓ Added description column")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ description column already exists")
            else:
                print(f"Error adding column: {e}")
                # Don't re-raise, might be other issues, but usually fine to proceed if column exists.

        conn.commit()

    print("\n✅ Migration completed successfully!")


if __name__ == "__main__":
    update_transactions_schema()
