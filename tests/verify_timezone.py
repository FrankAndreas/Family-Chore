
import os
import sys
from unittest.mock import MagicMock, patch
from apscheduler.triggers.cron import CronTrigger

# Add project root to sys.path
sys.path.append(os.getcwd())

# Mock database and other dependencies to avoid side effects during import
sys.modules["backend.database"] = MagicMock()
sys.modules["backend.routers"] = MagicMock()
sys.modules["backend.routers.analytics"] = MagicMock()
sys.modules["backend.migrations.manager"] = MagicMock()
sys.modules["backend.backup"] = MagicMock()

# Now import main
from backend import main  # noqa: E402


def test_scheduler_timezone():
    # Mock crud.get_system_setting to return a specific timezone
    mock_db = MagicMock()
    mock_setting = MagicMock()
    mock_setting.value = "Asia/Tokyo"  # Use non-default to verify verification

    with patch("backend.main.SessionLocal", return_value=mock_db):
        with patch("backend.main.crud.get_system_setting", return_value=mock_setting):
            with patch("backend.main.scheduler") as mock_scheduler:
                # Run startup
                main.on_startup()

                # Verify scheduler.configure was called with correct timezone
                mock_scheduler.configure.assert_called_with(
                    timezone="Asia/Tokyo")

                # Verify jobs added with correct timezone
                # We expect 2 add_job calls
                assert mock_scheduler.add_job.call_count == 2

                # Check arguments of first call (reset job)
                args, kwargs = mock_scheduler.add_job.call_args_list[0]
                trigger = kwargs.get('trigger')
                assert isinstance(trigger, CronTrigger)
                # CronTrigger timezone should be Asia/Tokyo
                assert str(trigger.timezone) == "Asia/Tokyo"

                print(
                    "✅ Verification Successful: Scheduler configured with 'Asia/Tokyo'")


if __name__ == "__main__":
    try:
        test_scheduler_timezone()
    except AssertionError as e:
        print(f"❌ Verification Failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
