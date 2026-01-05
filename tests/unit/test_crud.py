"""
Unit tests for CRUD operations - focusing on critical business logic.
"""
import pytest
from datetime import datetime
from backend import crud, models, schemas


class TestPointCalculation:
    """Test the core point calculation logic."""

    def test_complete_task_calculates_points_correctly(self, seeded_db):
        """Test that points are calculated as base_points * multiplier."""
        # Arrange
        teenager_role = seeded_db.query(models.Role).filter(
            models.Role.name == "Teenager"
        ).first()
        teenager_role.multiplier_value = 1.5

        user = models.User(
            nickname="TestTeen",
            login_pin="1234",
            role_id=teenager_role.id,
            current_points=0,
            lifetime_points=0
        )
        seeded_db.add(user)

        task = models.Task(
            name="Test Task",
            description="Test",
            base_points=10,
            assigned_role_id=teenager_role.id,
            schedule_type="daily",
            default_due_time="17:00"
        )
        seeded_db.add(task)
        seeded_db.commit()

        instance = models.TaskInstance(
            task_id=task.id,
            user_id=user.id,
            due_time=datetime.now(),
            status="PENDING"
        )
        seeded_db.add(instance)
        seeded_db.commit()

        # Act
        completed = crud.complete_task_instance(seeded_db, instance.id)

        # Assert
        assert completed.status == "COMPLETED"
        seeded_db.refresh(user)
        assert user.current_points == 15  # 10 * 1.5
        assert user.lifetime_points == 15

    def test_complete_task_creates_transaction(self, seeded_db):
        """Test that completing a task creates a transaction record."""
        # Arrange
        child_role = seeded_db.query(models.Role).filter(
            models.Role.name == "Child"
        ).first()

        user = models.User(
            nickname="TestChild",
            login_pin="1234",
            role_id=child_role.id,
            current_points=0,
            lifetime_points=0
        )
        seeded_db.add(user)

        task = models.Task(
            name="Chore",
            description="Test chore",
            base_points=20,
            assigned_role_id=child_role.id,
            schedule_type="daily",
            default_due_time="18:00"
        )
        seeded_db.add(task)
        seeded_db.commit()

        instance = models.TaskInstance(
            task_id=task.id,
            user_id=user.id,
            due_time=datetime.now(),
            status="PENDING"
        )
        seeded_db.add(instance)
        seeded_db.commit()

        # Act
        crud.complete_task_instance(seeded_db, instance.id)

        # Assert
        transaction = seeded_db.query(models.Transaction).filter(
            models.Transaction.reference_instance_id == instance.id
        ).first()

        assert transaction is not None
        assert transaction.type == "EARN"
        assert transaction.base_points_value == 20
        assert transaction.multiplier_used == 1.5  # Child default
        assert transaction.awarded_points == 30  # 20 * 1.5

    def test_complete_task_idempotent(self, seeded_db):
        """Test that completing an already completed task doesn't award points twice."""
        # Arrange
        admin_role = seeded_db.query(models.Role).filter(
            models.Role.name == "Admin"
        ).first()

        user = models.User(
            nickname="Admin",
            login_pin="1234",
            role_id=admin_role.id,
            current_points=0,
            lifetime_points=0
        )
        seeded_db.add(user)

        task = models.Task(
            name="Task",
            description="Test",
            base_points=10,
            assigned_role_id=admin_role.id,
            schedule_type="daily",
            default_due_time="17:00"
        )
        seeded_db.add(task)
        seeded_db.commit()

        instance = models.TaskInstance(
            task_id=task.id,
            user_id=user.id,
            due_time=datetime.now(),
            status="PENDING"
        )
        seeded_db.add(instance)
        seeded_db.commit()

        # Act - complete twice
        crud.complete_task_instance(seeded_db, instance.id)
        crud.complete_task_instance(seeded_db, instance.id)

        # Assert - points only awarded once
        seeded_db.refresh(user)
        assert user.current_points == 10
        assert user.lifetime_points == 10


class TestDailyReset:
    """Test daily task instance generation."""

    def test_generate_daily_instances_creates_for_assigned_role(self, seeded_db):
        """Test that daily reset creates instances for users with assigned role."""
        # Arrange
        child_role = seeded_db.query(models.Role).filter(
            models.Role.name == "Child"
        ).first()

        user1 = models.User(nickname="Child1", login_pin="1111", role_id=child_role.id)
        user2 = models.User(nickname="Child2", login_pin="2222", role_id=child_role.id)
        seeded_db.add_all([user1, user2])

        task = models.Task(
            name="Daily Chore",
            description="Test",
            base_points=10,
            assigned_role_id=child_role.id,
            schedule_type="daily",
            default_due_time="17:00"
        )
        seeded_db.add(task)
        seeded_db.commit()

        # Act
        count = crud.generate_daily_instances(seeded_db)

        # Assert
        assert count == 2  # One for each child
        instances = seeded_db.query(models.TaskInstance).all()
        assert len(instances) == 2

    def test_generate_daily_instances_prevents_duplicates(self, seeded_db):
        """Test that daily reset doesn't create duplicate instances for same day."""
        # Arrange
        teenager_role = seeded_db.query(models.Role).filter(
            models.Role.name == "Teenager"
        ).first()

        user = models.User(nickname="Teen", login_pin="1234", role_id=teenager_role.id)
        seeded_db.add(user)

        task = models.Task(
            name="Homework",
            description="Daily homework",
            base_points=15,
            assigned_role_id=teenager_role.id,
            schedule_type="daily",
            default_due_time="20:00"
        )
        seeded_db.add(task)
        seeded_db.commit()

        # Act - run daily reset twice
        count1 = crud.generate_daily_instances(seeded_db)
        count2 = crud.generate_daily_instances(seeded_db)

        # Assert
        assert count1 == 1
        assert count2 == 0  # No duplicates created
        instances = seeded_db.query(models.TaskInstance).all()
        assert len(instances) == 1


class TestInputValidation:
    """Test input validation at the schema level."""

    def test_user_pin_must_be_4_digits(self):
        """Test that PIN validation requires exactly 4 digits."""
        # Valid PIN
        valid_user = schemas.UserCreate(
            nickname="Test",
            login_pin="1234",
            role_id=1
        )
        assert valid_user.login_pin == "1234"

        # Invalid PINs should raise validation error
        with pytest.raises(ValueError):
            schemas.UserCreate(nickname="Test", login_pin="123", role_id=1)

        with pytest.raises(ValueError):
            schemas.UserCreate(nickname="Test", login_pin="12345", role_id=1)

        with pytest.raises(ValueError):
            schemas.UserCreate(nickname="Test", login_pin="abcd", role_id=1)

    def test_task_time_validation(self):
        """Test that task time must be in HH:MM format."""
        # Valid times
        valid_task = schemas.TaskCreate(
            name="Task",
            description="Test",
            base_points=10,
            assigned_role_id=1,
            schedule_type="daily",
            default_due_time="17:00"
        )
        assert valid_task.default_due_time == "17:00"

        # Invalid times should raise validation error
        with pytest.raises(ValueError):
            schemas.TaskCreate(
                name="Task",
                description="Test",
                base_points=10,
                assigned_role_id=1,
                schedule_type="daily",
                default_due_time="25:00"  # Invalid hour
            )

        with pytest.raises(ValueError):
            schemas.TaskCreate(
                name="Task",
                description="Test",
                base_points=10,
                assigned_role_id=1,
                schedule_type="daily",
                default_due_time="17:60"  # Invalid minute
            )

    def test_task_base_points_must_be_positive(self):
        """Test that base points must be greater than 0."""
        # Valid points
        valid_task = schemas.TaskCreate(
            name="Task",
            description="Test",
            base_points=1,
            assigned_role_id=1,
            schedule_type="daily",
            default_due_time="17:00"
        )
        assert valid_task.base_points == 1

        # Invalid points should raise validation error
        with pytest.raises(ValueError):
            schemas.TaskCreate(
                name="Task",
                description="Test",
                base_points=0,
                assigned_role_id=1,
                schedule_type="daily",
                default_due_time="17:00"
            )

        with pytest.raises(ValueError):
            schemas.TaskCreate(
                name="Task",
                description="Test",
                base_points=-10,
                assigned_role_id=1,
                schedule_type="daily",
                default_due_time="17:00"
            )
