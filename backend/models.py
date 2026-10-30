import datetime
from datetime import timezone
from sqlalchemy import Boolean, Integer, String, Float, ForeignKey, DateTime, Date, Text, true
from sqlalchemy.orm import mapped_column, relationship
from .database import Base

# System Settings (for family-wide configurations)


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = mapped_column(Integer, primary_key=True, index=True)
    # e.g., "default_language"
    key = mapped_column(String, unique=True, nullable=False)
    value = mapped_column(String, nullable=False)  # e.g., "en" or "de"
    description = mapped_column(Text, nullable=True)

# 1.1 Roles (Multiplier Configuration)


class Role(Base):
    __tablename__ = "roles"

    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String, unique=True, nullable=False)
    multiplier_value = mapped_column(Float, nullable=False, default=1.0)

    # Relationships
    users = relationship("User", back_populates="role")
    tasks = relationship("Task", back_populates="assigned_role")


# 1.2 Users (System Initialization & Goal Tracking)
class User(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True, index=True)
    role_id = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)
    nickname = mapped_column(String, unique=True, nullable=False)
    # The person in the family hub (spec 2026-10-30): login, name, language and parent/child come from there. None: a
    # row from before the hub, linked by name at the first sync
    hub_id = mapped_column(Integer, unique=True, nullable=True)
    # False: the hub no longer lists the person here; hidden with points and history until a parent deletes them
    is_active = mapped_column(Boolean, nullable=False, default=True, server_default=true())

    current_points = mapped_column(Integer, nullable=False, default=0)
    lifetime_points = mapped_column(Integer, nullable=False, default=0)

    current_goal_reward_id = mapped_column(
        Integer, ForeignKey("rewards.id"), nullable=True)

    # Notifications & Contact
    email = mapped_column(String, unique=True, nullable=True)
    notifications_enabled = mapped_column(Boolean, default=True)

    # Language preference (null = use system default)
    # e.g., "de", "en", or null
    preferred_language = mapped_column(String, nullable=True)

    # Gamification Polish
    current_streak = mapped_column(Integer, nullable=False, default=0)
    last_task_date = mapped_column(Date, nullable=True)

    # Relationships
    role = relationship("Role", back_populates="users")
    current_goal = relationship("Reward", foreign_keys=[
                                current_goal_reward_id])
    task_instances = relationship("TaskInstance", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    push_subscriptions = relationship("PushSubscription", back_populates="user", cascade="all, delete-orphan")


# 1.5 Rewards (Reward Hub Catalog)
class Reward(Base):
    __tablename__ = "rewards"

    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String, nullable=False)
    cost_points = mapped_column(Integer, nullable=False)
    description = mapped_column(Text)
    tier_level = mapped_column(Integer, default=0)


# 1.3 Tasks (Chore Templates)
class Task(Base):
    __tablename__ = "tasks"

    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String, nullable=False)
    description = mapped_column(Text, nullable=False)
    base_points = mapped_column(Integer, nullable=False)

    assigned_role_id = mapped_column(Integer, ForeignKey("roles.id"), nullable=True)

    # Scheduling
    schedule_type = mapped_column(String, nullable=False, default="daily")
    # e.g., "17:00" for daily, "Monday" for weekly, or ignored for recurring
    default_due_time = mapped_column(String, nullable=False)

    # Recurring task configuration (for schedule_type="recurring")
    # Min days between completions (e.g., 3)
    recurrence_min_days = mapped_column(Integer, nullable=True)
    # Max days between completions (e.g., 5)
    recurrence_max_days = mapped_column(Integer, nullable=True)

    # V1.1 Fields
    requires_photo_verification = mapped_column(Boolean, default=False)

    # Relationships
    assigned_role = relationship("Role", back_populates="tasks")
    instances = relationship("TaskInstance", back_populates="task")


# 1.4 Task_Instances (Task Execution & Reporting)
class TaskInstance(Base):
    __tablename__ = "task_instances"

    id = mapped_column(Integer, primary_key=True, index=True)
    task_id = mapped_column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    due_time = mapped_column(DateTime, nullable=False)
    completed_at = mapped_column(DateTime, nullable=True)
    status = mapped_column(String, nullable=False, default="PENDING", index=True)

    completion_photo_url = mapped_column(String, nullable=True)

    # Relationships
    task = relationship("Task", back_populates="instances")
    user = relationship("User", back_populates="task_instances")
    transaction = relationship(
        "Transaction", back_populates="reference_instance", uselist=False)


# 2.1 Transactions (Audit & Reporting)
class Transaction(Base):
    __tablename__ = "transactions"

    id = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    type = mapped_column(String, nullable=False)  # 'EARN', 'REDEEM', or 'PENALTY'

    base_points_value = mapped_column(Integer, nullable=False)
    multiplier_used = mapped_column(Float, nullable=False)
    awarded_points = mapped_column(Integer, nullable=False)
    description = mapped_column(String, nullable=True)  # Snapshot of task/reward name

    reference_instance_id = mapped_column(
        Integer, ForeignKey("task_instances.id"), nullable=True)

    timestamp = mapped_column(DateTime, nullable=False,
                              default=lambda: datetime.datetime.now(timezone.utc), index=True)

    # Relationships
    user = relationship("User", back_populates="transactions")
    reference_instance = relationship(
        "TaskInstance", back_populates="transaction")


# 3.0 Notifications (System & User Alerts)
class Notification(Base):
    __tablename__ = "notifications"

    id = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 'TASK_ASSIGNED', 'TASK_COMPLETED', 'REWARD_REDEEMED', 'SYSTEM'
    type = mapped_column(String, nullable=False)
    title = mapped_column(String, nullable=False)
    message = mapped_column(String, nullable=False)

    read = mapped_column(Boolean, default=False)

    created_at = mapped_column(DateTime, nullable=False,
                               default=lambda: datetime.datetime.now(timezone.utc))
    # JSON string for extra data (e.g. {"task_id": 123})
    data = mapped_column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="notifications")


# 3.1 Web Push Subscriptions
class PushSubscription(Base):
    __tablename__ = "push_subscriptions"

    id = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    endpoint = mapped_column(String, unique=True, nullable=False)
    p256dh = mapped_column(String, nullable=False)
    auth = mapped_column(String, nullable=False)

    created_at = mapped_column(DateTime, nullable=False, default=lambda: datetime.datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="push_subscriptions")
