from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from datetime import datetime

# --- System Settings Schemas ---


class SystemSettingsBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None


class SystemSettings(SystemSettingsBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserLanguageUpdate(BaseModel):
    preferred_language: Optional[str] = Field(
        None, pattern=r'^(en|de)?$', description="Language code: 'en', 'de', or null for default")

# --- Role Schemas ---

# --- Role Schemas ---


class RoleBase(BaseModel):
    name: str
    multiplier_value: float


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    multiplier_value: float


class Role(RoleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# --- User Schemas ---


class UserBase(BaseModel):
    nickname: str
    role_id: int


class UserCreate(UserBase):
    login_pin: str = Field(..., pattern=r'^\d{4}$', description="4-digit PIN")

    @field_validator('login_pin')
    @classmethod
    def validate_pin(cls, v):
        if not v.isdigit() or len(v) != 4:
            raise ValueError('PIN must be exactly 4 digits')
        return v


class UserLogin(BaseModel):
    nickname: str
    login_pin: str


class User(UserBase):
    id: int
    current_points: int
    lifetime_points: int
    current_goal_reward_id: Optional[int] = None
    preferred_language: Optional[str] = None
    role: Role

    model_config = ConfigDict(from_attributes=True)


# --- Task Schemas ---
class TaskBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Task name")
    description: str = Field(..., min_length=1, max_length=500, description="Task description")
    base_points: int = Field(..., gt=0, le=1000, description="Base points (1-1000)")
    assigned_role_id: Optional[int] = None
    schedule_type: str = "daily"
    default_due_time: str = Field(
        ...,
        description="Time in HH:MM format for daily, day name for weekly, or any value for recurring"
    )

    # Recurring task fields
    recurrence_min_days: Optional[int] = Field(
        None, ge=1, le=365, description="Minimum days between completions (recurring only)")
    recurrence_max_days: Optional[int] = Field(
        None, ge=1, le=365, description="Maximum days between completions (recurring only)")

    @model_validator(mode='after')
    def validate_schedule_and_time(self):
        """Validate default_due_time and recurrence fields based on schedule_type."""
        if self.schedule_type == "daily":
            # Validate HH:MM format
            try:
                hour, minute = map(int, self.default_due_time.split(':'))
                if not (0 <= hour < 24 and 0 <= minute < 60):
                    raise ValueError('Hour must be 0-23 and minute must be 0-59')
            except (ValueError, AttributeError):
                raise ValueError('For daily tasks, default_due_time must be in HH:MM format (00:00-23:59)')
        elif self.schedule_type == "weekly":
            # Validate day of week
            valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            if self.default_due_time not in valid_days:
                raise ValueError(f'For weekly tasks, default_due_time must be a day name: {", ".join(valid_days)}')
        elif self.schedule_type == "recurring":
            # Validate recurrence fields
            if self.recurrence_min_days is None or self.recurrence_max_days is None:
                raise ValueError(
                    'For recurring tasks, both recurrence_min_days and recurrence_max_days must be specified')
            if self.recurrence_min_days > self.recurrence_max_days:
                raise ValueError('recurrence_min_days must be less than or equal to recurrence_max_days')
        else:
            raise ValueError('schedule_type must be "daily", "weekly", or "recurring"')

        return self


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task. All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    base_points: Optional[int] = Field(None, gt=0, le=1000)
    assigned_role_id: Optional[int] = None
    schedule_type: Optional[str] = None
    default_due_time: Optional[str] = None
    recurrence_min_days: Optional[int] = Field(None, ge=1, le=365)
    recurrence_max_days: Optional[int] = Field(None, ge=1, le=365)

    @model_validator(mode='after')
    def validate_update_fields(self):
        """Validate schedule_type and related fields if they're being updated."""
        # If schedule_type is being updated, validate related fields
        if self.schedule_type:
            if self.schedule_type == "daily" and self.default_due_time:
                try:
                    hour, minute = map(int, self.default_due_time.split(':'))
                    if not (0 <= hour < 24 and 0 <= minute < 60):
                        raise ValueError('Hour must be 0-23 and minute must be 0-59')
                except (ValueError, AttributeError):
                    raise ValueError('For daily tasks, default_due_time must be in HH:MM format')
            elif self.schedule_type == "weekly" and self.default_due_time:
                valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                if self.default_due_time not in valid_days:
                    raise ValueError(f'For weekly tasks, default_due_time must be a day name: {", ".join(valid_days)}')
            elif self.schedule_type == "recurring":
                if self.recurrence_min_days and self.recurrence_max_days:
                    if self.recurrence_min_days > self.recurrence_max_days:
                        raise ValueError('recurrence_min_days must be <= recurrence_max_days')
        return self


class Task(TaskBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# --- TaskInstance Schemas ---


class TaskInstanceBase(BaseModel):
    task_id: int
    user_id: int
    due_time: datetime  # ISO format
    status: str


class TaskInstance(TaskInstanceBase):
    id: int
    completed_at: Optional[datetime] = None
    completion_photo_url: Optional[str] = None
    task: Optional[Task] = None  # Include task details for Family Dashboard
    user: Optional[User] = None  # Include user details

    model_config = ConfigDict(from_attributes=True)

# --- Reward Schemas ---


class RewardBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Reward name")
    cost_points: int = Field(..., gt=0, le=10000, description="Cost in points (1-10000)")
    description: Optional[str] = Field(None, max_length=500)
    tier_level: int = Field(default=0, ge=0, le=10, description="Tier level (0-10)")


class RewardCreate(RewardBase):
    pass


class Reward(RewardBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RedemptionResponse(BaseModel):
    """Response from reward redemption endpoint."""
    success: bool
    transaction_id: Optional[int] = None
    reward_name: Optional[str] = None
    points_spent: Optional[int] = None
    remaining_points: Optional[int] = None
    error: Optional[str] = None


class SplitContribution(BaseModel):
    """A single user's contribution to a split redemption."""
    user_id: int
    points: int = Field(..., ge=0, description="Points this user contributes (0 or more)")


class SplitRedemptionRequest(BaseModel):
    """Request to redeem a reward with contributions from multiple users."""
    contributions: list[SplitContribution] = Field(..., min_length=1)


class SplitRedemptionResponse(BaseModel):
    """Response from split redemption endpoint."""
    success: bool
    reward_name: Optional[str] = None
    total_points: Optional[int] = None
    transactions: Optional[list[dict]] = None  # List of {user_id, user_name, points, transaction_id}
    error: Optional[str] = None


# --- Transaction Schemas ---


class TransactionBase(BaseModel):
    user_id: int
    type: str  # 'EARN' or 'REDEEM'
    base_points_value: int
    multiplier_used: float
    awarded_points: int
    description: Optional[str] = None
    reference_instance_id: Optional[int] = None
    timestamp: datetime


class Transaction(TransactionBase):
    id: int
    # We might want to include nested objects for display, but for now let's keep it simple
    # or use separate schemas if needed for detailed history views.
    # For now, let's include the user nickname if possible via a validator or separate field,
    # but strictly speaking the model has a relationship.
    # Let's stick to the base fields first.

    model_config = ConfigDict(from_attributes=True)


# --- Task Import/Export Schemas ---


class TaskImportItem(BaseModel):
    """Single task in import format - uses role name instead of ID for readability."""
    name: str = Field(..., min_length=1, max_length=100, description="Task name")
    description: str = Field(..., min_length=1, max_length=500, description="Task description")
    base_points: int = Field(..., gt=0, le=1000, description="Base points (1-1000)")
    assigned_role: Optional[str] = Field(None, description="Role name (e.g., 'Child', 'Teenager')")
    schedule_type: str = Field("daily", description="Schedule type: daily, weekly, or recurring")
    default_due_time: str = Field(
        ...,
        description="Time in HH:MM format for daily, day name for weekly, or any value for recurring"
    )
    recurrence_min_days: Optional[int] = Field(None, ge=1, le=365)
    recurrence_max_days: Optional[int] = Field(None, ge=1, le=365)

    @model_validator(mode='after')
    def validate_schedule_and_time(self):
        """Validate default_due_time and recurrence fields based on schedule_type."""
        # Normalize localized schedule types
        if self.schedule_type.lower() == "täglich":
            self.schedule_type = "daily"
        elif self.schedule_type.lower() == "wöchentlich":
            self.schedule_type = "weekly"

        if self.schedule_type == "daily":
            try:
                hour, minute = map(int, self.default_due_time.split(':'))
                if not (0 <= hour < 24 and 0 <= minute < 60):
                    raise ValueError('Hour must be 0-23 and minute must be 0-59')
            except (ValueError, AttributeError):
                raise ValueError('For daily tasks, default_due_time must be in HH:MM format')
        elif self.schedule_type == "weekly":
            # Check if it's a valid day name
            valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            if self.default_due_time in valid_days:
                return self

            # Check if it looks like a time (HH:MM) - if so, convert to recurring (weekly = 7 days)
            try:
                hour, minute = map(int, self.default_due_time.split(':'))
                if 0 <= hour < 24 and 0 <= minute < 60:
                    # It's a valid time, but schedule is weekly.
                    # Convert to recurring task with 7 days interval
                    self.schedule_type = "recurring"
                    self.recurrence_min_days = 7
                    self.recurrence_max_days = 7
                    # default_due_time remains HH:MM which is valid for recurring tasks?
                    # Actually, recurring tasks usually don't have a specific due time in the same way,
                    # but let's check TaskBase. It has default_due_time.
                    # Wait, for recurring tasks, 'default_due_time' interpretation depends on implementation.
                    # If we look at TaskBase, it says: "any value for recurring".
                    # So keeping HH:MM is fine.
                    return self
            except (ValueError, AttributeError):
                pass

            raise ValueError('For weekly tasks, default_due_time must be a day name (e.g. Monday)')
        elif self.schedule_type == "recurring":
            if self.recurrence_min_days is None or self.recurrence_max_days is None:
                raise ValueError('For recurring tasks, both recurrence_min_days and recurrence_max_days required')
            if self.recurrence_min_days > self.recurrence_max_days:
                raise ValueError('recurrence_min_days must be <= recurrence_max_days')
        else:
            raise ValueError('schedule_type must be "daily", "weekly", or "recurring"')
        return self


class TasksImport(BaseModel):
    """Import payload for bulk task creation."""
    tasks: List[TaskImportItem]
    skip_duplicates: bool = Field(False, description="Skip tasks with names that already exist")


class TaskExportItem(BaseModel):
    """Single task in export format - uses role name for readability."""
    name: str
    description: str
    base_points: int
    assigned_role: Optional[str] = None
    schedule_type: str
    default_due_time: str
    recurrence_min_days: Optional[int] = None
    recurrence_max_days: Optional[int] = None


class TasksExport(BaseModel):
    """Export payload containing all tasks."""
    version: str = "1.0"
    exported_at: str
    tasks: List[TaskExportItem]
