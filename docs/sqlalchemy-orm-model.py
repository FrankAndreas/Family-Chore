import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from typing import Optional

# --- Database Setup (SQLite) ---

# Define the path for the SQLite database file
# This will create the file if it doesn't exist.
SQLALCHEMY_DATABASE_URL = "sqlite:///./chorespec_mvp.db"

# Create the SQLAlchemy engine. check_same_thread is needed for SQLite multi-threading
# in web applications, though generally for FastAPI, you run database operations in a thread pool.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Each instance of the SessionLocal class will be a database session.
# The bind parameter tells the session what engine to use.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class which ORM models will inherit from
Base = declarative_base()


# --- ORM Models (Based on data_model.md) ---

# 1.1 Roles (Multiplier Configuration)
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # e.g., 'Admin', 'Teenager' (AC 1.3)
    # multiplier_value >= 0.1 (AC 2.4)
    multiplier_value = Column(Float, nullable=False, default=1.0)

    # Relationships
    users = relationship("User", back_populates="role")
    tasks = relationship("Task", back_populates="assigned_role")


# 1.2 Users (System Initialization & Goal Tracking)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # Links to roles (AC 1.3)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    nickname = Column(String, unique=True, nullable=False) # AC 1.2
    login_pin = Column(String, nullable=False) # AC 1.2
    
    # Point tracking (AC 5.2, V1.1 AC 8.3)
    current_points = Column(Integer, nullable=False, default=0)
    lifetime_points = Column(Integer, nullable=False, default=0)
    
    # Goal Tracking (AC 5.1)
    current_goal_reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=True)

    # Relationships
    role = relationship("Role", back_populates="users")
    current_goal = relationship("Reward", foreign_keys=[current_goal_reward_id])
    task_instances = relationship("TaskInstance", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")


# 1.5 Rewards (Reward Hub Catalog)
class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cost_points = Column(Integer, nullable=False) # AC 5.2
    description = Column(Text)
    tier_level = Column(Integer, default=0) # V1.1 AC 8.1

    # Note: Relationship back to User.current_goal is defined on User model


# 1.3 Tasks (Chore Templates)
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # AC 3.2
    description = Column(Text, nullable=False) # AC 3.2
    base_points = Column(Integer, nullable=False) # AC 3.2
    
    # Links to the target role (AC 3.3)
    assigned_role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)

    # Scheduling (AC 3.4)
    schedule_type = Column(String, nullable=False, default="daily")
    default_due_time = Column(String, nullable=False) # e.g., "17:00"

    # V1.1 Fields (Optional for MVP implementation, but included for complete schema)
    requires_photo_verification = Column(Text, default="false") # V1.1 AC 7.1

    # Relationships
    assigned_role = relationship("Role", back_populates="tasks")
    instances = relationship("TaskInstance", back_populates="task")


# 1.4 Task_Instances (Task Execution & Reporting)
class TaskInstance(Base):
    __tablename__ = "task_instances"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Scheduling & Status (AC 3.4, 4.1, 4.2)
    due_time = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    # Status: PENDING, COMPLETED, OVERDUE, PENDING_REVIEW (V1.1 AC 7.3)
    status = Column(String, nullable=False, default="PENDING")
    
    # V1.1 Field
    completion_photo_url = Column(String, nullable=True)

    # Relationships
    task = relationship("Task", back_populates="instances")
    user = relationship("User", back_populates="task_instances")
    transaction = relationship("Transaction", back_populates="reference_instance", uselist=False)


# 2.1 Transactions (Audit & Reporting)
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Type: EARN or REDEEM
    type = Column(String, nullable=False)
    
    # Effort and Reward Data (AC 4.3, 4.4)
    base_points_value = Column(Integer, nullable=False)
    multiplier_used = Column(Float, nullable=False)
    awarded_points = Column(Integer, nullable=False)
    
    # Link to the completed task instance
    reference_instance_id = Column(Integer, ForeignKey("task_instances.id"), nullable=True)
    
    timestamp = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="transactions")
    reference_instance = relationship("TaskInstance", back_populates="transaction")


# Function to create all tables in the database
def create_tables():
    Base.metadata.create_all(bind=engine)

# Example usage (to be run once to initialize the database):
# if __name__ == "__main__":
#     create_tables()