from typing import Optional
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
