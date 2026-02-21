
"""
Unit tests for Analytics operations.
"""
from datetime import datetime, timedelta
from backend import models


class TestAnalytics:
    """Test analytics data retrieval."""

    def test_weekly_activity_returns_correct_data(self, client, seeded_db):
        """Test weekly activity aggregation."""
        # Arrange
        child_role = seeded_db.query(models.Role).filter(
            models.Role.name == "Child"
        ).first()

        user = models.User(
            nickname="AnalyticsUser",
            login_pin="1234",
            role_id=child_role.id,
            current_points=0,
            lifetime_points=0
        )
        seeded_db.add(user)
        seeded_db.commit()

        # Create tasks completed at different times
        # 1. Today (included)
        t1 = models.TaskInstance(
            task_id=1,  # Assume task 1 exists from seed or we can create it
            user_id=user.id,
            status="COMPLETED",
            due_time=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        # 2. Yesterday (included)
        t2 = models.TaskInstance(
            task_id=1,
            user_id=user.id,
            status="COMPLETED",
            due_time=datetime.utcnow(),
            completed_at=datetime.utcnow() - timedelta(days=1)
        )
        # 3. 8 days ago (excluded)
        t3 = models.TaskInstance(
            task_id=1,
            user_id=user.id,
            status="COMPLETED",
            due_time=datetime.utcnow(),
            completed_at=datetime.utcnow() - timedelta(days=8)
        )

        # We need a task for FK constraint usually, but let's check
        # if models enforce it strongly in sqlite without enabling it explicitly.
        # Actually, let's just create a dummy task to be safe.
        task = models.Task(
            name="Dummy Task",
            description="A test task",
            base_points=10,
            assigned_role_id=None,
            default_due_time="17:00"
        )
        seeded_db.add(task)
        seeded_db.commit()
        seeded_db.refresh(task)

        t1.task_id = task.id
        t2.task_id = task.id
        t3.task_id = task.id

        seeded_db.add_all([t1, t2, t3])
        seeded_db.commit()

        # Act
        response = client.get("/analytics/weekly")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 7  # Last 7 days

        # Verify counts
        today_str = datetime.now().date().strftime("%Y-%m-%d")
        yesterday_str = (datetime.now().date() -
                         timedelta(days=1)).strftime("%Y-%m-%d")

        found_today = False
        found_yesterday = False

        for entry in data:
            if entry["date"] == today_str:
                assert entry[user.nickname] == 1
                found_today = True
            elif entry["date"] == yesterday_str:
                assert entry[user.nickname] == 1
                found_yesterday = True
            else:
                # Should be empty for this user or 0 if we init 0
                # (logic says it inits empty dict)
                assert user.nickname not in entry or entry[user.nickname] == 0
        assert found_today
        assert found_yesterday

    def test_points_distribution_returns_correct_data(self, client, seeded_db):
        """Test points distribution endpoint."""
        # Arrange
        child_role = seeded_db.query(models.Role).filter(
            models.Role.name == "Child"
        ).first()

        user1 = models.User(
            nickname="UserHigh",
            login_pin="1111",
            role_id=child_role.id,
            current_points=100,
            lifetime_points=1000
        )
        user2 = models.User(
            nickname="UserLow",
            login_pin="2222",
            role_id=child_role.id,
            current_points=50,
            lifetime_points=200
        )
        seeded_db.add_all([user1, user2])
        seeded_db.commit()

        # Act
        response = client.get("/analytics/distribution")

        # Assert
        assert response.status_code == 200
        data = response.json()
        # Verify we find our users
        user1_data = next(
            (item for item in data if item["name"] == "UserHigh"), None
        )
        user2_data = next(
            (item for item in data if item["name"] == "UserLow"), None
        )

        assert user1_data is not None
        assert user1_data["value"] == 1000
        assert user1_data["role"] == "Child"

        assert user2_data is not None
        assert user2_data["value"] == 200
