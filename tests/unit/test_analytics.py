
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

    def test_heatmap_returns_correct_days_and_counts(self, client, seeded_db):
        """Test heatmap returns per-user, per-day counts for the requested window."""
        child_role = seeded_db.query(models.Role).filter(
            models.Role.name == "Child"
        ).first()

        user = models.User(
            nickname="HeatmapUser",
            login_pin="4321",
            role_id=child_role.id,
            current_points=0,
            lifetime_points=0,
        )
        seeded_db.add(user)
        seeded_db.commit()

        task = models.Task(
            name="Heatmap Task",
            description="For heatmap testing",
            base_points=5,
            assigned_role_id=None,
            default_due_time="08:00",
        )
        seeded_db.add(task)
        seeded_db.commit()
        seeded_db.refresh(task)

        # Task completed today (included)
        t1 = models.TaskInstance(
            task_id=task.id,
            user_id=user.id,
            status="COMPLETED",
            due_time=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        # Task completed 5 days ago (included in default 30-day window)
        t2 = models.TaskInstance(
            task_id=task.id,
            user_id=user.id,
            status="COMPLETED",
            due_time=datetime.utcnow(),
            completed_at=datetime.utcnow() - timedelta(days=5),
        )
        # Task completed 40 days ago (excluded from 30-day window)
        t3 = models.TaskInstance(
            task_id=task.id,
            user_id=user.id,
            status="COMPLETED",
            due_time=datetime.utcnow(),
            completed_at=datetime.utcnow() - timedelta(days=40),
        )
        seeded_db.add_all([t1, t2, t3])
        seeded_db.commit()

        response = client.get("/analytics/heatmap", params={"days": 30})
        assert response.status_code == 200

        data = response.json()
        assert "users" in data
        assert len(data["users"]) >= 1

        heatmap_user = next(
            (u for u in data["users"] if u["nickname"] == "HeatmapUser"), None
        )
        assert heatmap_user is not None
        assert len(heatmap_user["days"]) == 30

        today_str = datetime.now().date().strftime("%Y-%m-%d")
        five_ago_str = (
            datetime.now().date() - timedelta(days=5)
        ).strftime("%Y-%m-%d")

        today_entry = next(
            (d for d in heatmap_user["days"] if d["date"] == today_str), None
        )
        assert today_entry is not None
        assert today_entry["count"] == 1

        five_ago_entry = next(
            (d for d in heatmap_user["days"] if d["date"] == five_ago_str), None
        )
        assert five_ago_entry is not None
        assert five_ago_entry["count"] == 1

        # The 40-days-ago task should NOT appear in any of the 30 days
        total = sum(d["count"] for d in heatmap_user["days"])
        assert total == 2

    def test_summary_returns_streaks_and_top_performer(self, client, seeded_db):
        """Test summary returns top performer and streak leaderboard."""
        child_role = seeded_db.query(models.Role).filter(
            models.Role.name == "Child"
        ).first()

        user_a = models.User(
            nickname="SummaryAlice",
            login_pin="1111",
            role_id=child_role.id,
            current_points=0,
            lifetime_points=0,
            current_streak=5,
        )
        user_b = models.User(
            nickname="SummaryBob",
            login_pin="2222",
            role_id=child_role.id,
            current_points=0,
            lifetime_points=0,
            current_streak=2,
        )
        seeded_db.add_all([user_a, user_b])
        seeded_db.commit()

        task = models.Task(
            name="Summary Task",
            description="For summary testing",
            base_points=10,
            assigned_role_id=None,
            default_due_time="09:00",
        )
        seeded_db.add(task)
        seeded_db.commit()
        seeded_db.refresh(task)

        # Alice completes 3 tasks this week, Bob completes 1
        for _ in range(3):
            seeded_db.add(models.TaskInstance(
                task_id=task.id,
                user_id=user_a.id,
                status="COMPLETED",
                due_time=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            ))
        seeded_db.add(models.TaskInstance(
            task_id=task.id,
            user_id=user_b.id,
            status="COMPLETED",
            due_time=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        ))
        seeded_db.commit()

        response = client.get("/analytics/summary")
        assert response.status_code == 200

        data = response.json()
        assert data["week_total_tasks"] >= 4  # at least our 4

        # Top performer should be Alice
        assert data["top_performer"]["nickname"] == "SummaryAlice"
        assert data["top_performer"]["count"] >= 3

        # Streaks should be ordered desc — Alice (5) before Bob (2)
        alice_streak = next(
            (s for s in data["streaks"] if s["nickname"] == "SummaryAlice"), None
        )
        bob_streak = next(
            (s for s in data["streaks"] if s["nickname"] == "SummaryBob"), None
        )
        assert alice_streak is not None
        assert alice_streak["current_streak"] == 5
        assert bob_streak is not None
        assert bob_streak["current_streak"] == 2

    def test_heatmap_day_details_returns_task_names(self, client, seeded_db):
        """Test heatmap/details returns task names for a user on a given date."""
        child_role = seeded_db.query(models.Role).filter(
            models.Role.name == "Child"
        ).first()

        user = models.User(
            nickname="DetailUser",
            login_pin="9999",
            role_id=child_role.id,
            current_points=0,
            lifetime_points=0,
        )
        seeded_db.add(user)
        seeded_db.commit()

        task_a = models.Task(
            name="Wash Dishes",
            description="Detail test A",
            base_points=10,
            assigned_role_id=None,
            default_due_time="08:00",
        )
        task_b = models.Task(
            name="Vacuum Room",
            description="Detail test B",
            base_points=15,
            assigned_role_id=None,
            default_due_time="09:00",
        )
        seeded_db.add_all([task_a, task_b])
        seeded_db.commit()
        seeded_db.refresh(task_a)
        seeded_db.refresh(task_b)

        now = datetime.utcnow()
        seeded_db.add(models.TaskInstance(
            task_id=task_a.id,
            user_id=user.id,
            status="COMPLETED",
            due_time=now,
            completed_at=now,
        ))
        seeded_db.add(models.TaskInstance(
            task_id=task_b.id,
            user_id=user.id,
            status="COMPLETED",
            due_time=now,
            completed_at=now,
        ))
        seeded_db.commit()

        today_str = now.date().strftime("%Y-%m-%d")
        response = client.get(
            "/analytics/heatmap/details",
            params={"user_id": user.id, "date": today_str},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["nickname"] == "DetailUser"
        assert data["date"] == today_str
        assert len(data["tasks"]) == 2

        names = {t["task_name"] for t in data["tasks"]}
        assert "Wash Dishes" in names
        assert "Vacuum Room" in names

        points = {t["task_name"]: t["base_points"] for t in data["tasks"]}
        assert points["Wash Dishes"] == 10
        assert points["Vacuum Room"] == 15
