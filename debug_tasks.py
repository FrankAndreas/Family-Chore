import sqlite3
import pandas as pd
from tabulate import tabulate

def check_tasks():
    conn = sqlite3.connect('chorespec_mvp.db')
    try:
        # Get all tasks
        df = pd.read_sql_query("SELECT id, name, description, requires_photo_verification, recurrence_min_days, recurrence_max_days FROM tasks", conn)
        if df.empty:
            print("No tasks found in the database.")
        else:
            print(f"Found {len(df)} tasks:")
            print(tabulate(df, headers='keys', tablefmt='psql'))
            
        # Check task instances if any
        df_instances = pd.read_sql_query("SELECT id, task_id, status, due_time FROM task_instances", conn)
        if df_instances.empty:
            print("\nNo task instances found.")
        else:
            print(f"\nFound {len(df_instances)} task instances:")
            print(tabulate(df_instances, headers='keys', tablefmt='psql'))
            
    except Exception as e:
        print(f"Error reading database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_tasks()
