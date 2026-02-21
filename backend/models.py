import datetime
from datetime import timezone
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, Text
from sqlalchemy.orm import relationship
from .database import Base

# System Settings (for family-wide configurations)


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)  # e.g., "default_language"
    value = Column(String, nullable=False)  # e.g., "en" or "de"
    description = Column(Text, nullable=True)

# 1.1 Roles (Multiplier Configuration)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    multiplier_value = Column(Float, nullable=False, default=1.0)

    # Relationships
    users = relationship("User", back_populates="role")
    tasks = relationship("Task", back_populates="assigned_role")


# 1.2 Users (System Initialization & Goal Tracking)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    nickname = Column(String, unique=True, nullable=False)
    login_pin = Column(String, nullable=False)

    current_points = Column(Integer, nullable=False, default=0)
    lifetime_points = Column(Integer, nullable=False, default=0)

    current_goal_reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=True)

    # Language preference (null = use system default)
    preferred_language = Column(String, nullable=True)  # e.g., "de", "en", or null

    # Gamification Polish
    current_streak = Column(Integer, nullable=False, default=0)
    last_task_date = Column(Date, nullable=True)

    # Relationships
    role = relationship("Role", back_populates="users")
    current_goal = relationship("Reward", foreign_keys=[current_goal_reward_id])
    task_instances = relationship("TaskInstance", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    notifications = relationship("Notification", back_populates="user")


# 1.5 Rewards (Reward Hub Catalog)
class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cost_points = Column(Integer, nullable=False)
    description = Column(Text)
    tier_level = Column(Integer, default=0)


# 1.3 Tasks (Chore Templates)
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    base_points = Column(Integer, nullable=False)

    assigned_role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)

    # Scheduling
    schedule_type = Column(String, nullable=False, default="daily")
    # e.g., "17:00" for daily, "Monday" for weekly, or ignored for recurring
    default_due_time = Column(String, nullable=False)

    # Recurring task configuration (for schedule_type="recurring")
    recurrence_min_days = Column(Integer, nullable=True)  # Min days between completions (e.g., 3)
    recurrence_max_days = Column(Integer, nullable=True)  # Max days between completions (e.g., 5)

    # V1.1 Fields
    requires_photo_verification = Column(Integer, default=0)  # 0=false, 1=true

    # Relationships
    assigned_role = relationship("Role", back_populates="tasks")
    instances = relationship("TaskInstance", back_populates="task")


# 1.4 Task_Instances (Task Execution & Reporting)
class TaskInstance(Base):
    __tablename__ = "task_instances"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    due_time = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="PENDING")

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

    type = Column(String, nullable=False)  # 'EARN' or 'REDEEM'

    base_points_value = Column(Integer, nullable=False)
    multiplier_used = Column(Float, nullable=False)
    awarded_points = Column(Integer, nullable=False)
    description = Column(String, nullable=True)  # Snapshot of task/reward name

    reference_instance_id = Column(Integer, ForeignKey("task_instances.id"), nullable=True)

    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="transactions")
    reference_instance = relationship("TaskInstance", back_populates="transaction")


# 3.0 Notifications (System & User Alerts)
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    type = Column(String, nullable=False)  # 'TASK_ASSIGNED', 'TASK_COMPLETED', 'REWARD_REDEEMED', 'SYSTEM'
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)

    read = Column(Integer, default=0)

    created_at = Column(DateTime, nullable=False, default=lambda: datetime.datetime.now(timezone.utc))
    data = Column(Text, nullable=True)  # JSON string for extra data (e.g. {"task_id": 123})

    # Relationships
    user = relationship("User", back_populates="notifications")
