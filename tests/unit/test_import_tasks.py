import pytest
from pydantic import ValidationError
from backend.schemas import TaskImportItem


def test_valid_daily_task():
    """Test standard daily task creation."""
    item = TaskImportItem(
        name="Dishes",
        description="Wash dishes",
        base_points=10,
        schedule_type="daily",
        default_due_time="20:00"
    )
    assert item.schedule_type == "daily"
    assert item.default_due_time == "20:00"


def test_valid_weekly_task_day_name():
    """Test standard weekly task with day name."""
    item = TaskImportItem(
        name="Trash",
        description="Take out trash",
        base_points=20,
        schedule_type="weekly",
        default_due_time="Monday"
    )
    assert item.schedule_type == "weekly"
    assert item.default_due_time == "Monday"


def test_valid_recurring_task():
    """Test standard recurring task."""
    item = TaskImportItem(
        name="Mow Lawn",
        description="Cut the grass",
        base_points=50,
        schedule_type="recurring",
        default_due_time="Any",
        recurrence_min_days=7,
        recurrence_max_days=10
    )
    assert item.schedule_type == "recurring"
    assert item.recurrence_min_days == 7
    assert item.recurrence_max_days == 10


def test_localized_daily():
    """Test 'täglich' converts to 'daily'."""
    item = TaskImportItem(
        name="Zähneputzen",
        description="Brush teeth",
        base_points=5,
        schedule_type="täglich",
        default_due_time="08:00"
    )
    assert item.schedule_type == "daily"


def test_localized_weekly():
    """Test 'wöchentlich' converts to 'weekly'."""
    item = TaskImportItem(
        name="Staubsaugen",
        description="Vacuum",
        base_points=30,
        schedule_type="wöchentlich",
        default_due_time="Saturday"
    )
    assert item.schedule_type == "weekly"


def test_smart_conversion_weekly_time():
    """Test weekly task with HH:MM converts to recurring 7 days."""
    item = TaskImportItem(
        name="Weekly Meeting",
        description="Family meeting",
        base_points=100,
        schedule_type="weekly",
        default_due_time="18:00"
    )
    assert item.schedule_type == "recurring"
    assert item.recurrence_min_days == 7
    assert item.recurrence_max_days == 7
    # Time should remain preserved
    assert item.default_due_time == "18:00"


def test_invalid_daily_time():
    """Test invalid time format for daily task."""
    with pytest.raises(ValidationError) as excinfo:
        TaskImportItem(
            name="Bad Time",
            description="...",
            base_points=10,
            schedule_type="daily",
            default_due_time="25:00"
        )
    assert "Hour must be 0-23" in str(excinfo.value)

    with pytest.raises(ValidationError) as excinfo:
        TaskImportItem(
            name="Bad Format",
            description="...",
            base_points=10,
            schedule_type="daily",
            default_due_time="Morning"
        )
    assert "HH:MM format" in str(excinfo.value)


def test_invalid_weekly_day():
    """Test invalid day name for weekly task."""
    with pytest.raises(ValidationError) as excinfo:
        TaskImportItem(
            name="Bad Day",
            description="...",
            base_points=10,
            schedule_type="weekly",
            default_due_time="NotADay"
        )
    assert "must be a day name" in str(excinfo.value)


def test_invalid_recurring_missing_fields():
    """Test recurring task missing min/max days."""
    with pytest.raises(ValidationError) as excinfo:
        TaskImportItem(
            name="Bad Recurring",
            description="...",
            base_points=10,
            schedule_type="recurring",
            default_due_time="Any"
        )
    assert "validation error" in str(excinfo.value)
    # Exact message might be Pydantic's default or ours depending on path
    # Our validator raises: 'both recurrence_min_days and recurrence_max_days required'


def test_normalize_mixed_case():
    """Test mixed case normalization for localized inputs."""
    item = TaskImportItem(
        name="Test",
        description="...",
        base_points=10,
        schedule_type="TäGLiCh",  # weird casing
        default_due_time="09:00"
    )
    assert item.schedule_type == "daily"  # Should normalize
