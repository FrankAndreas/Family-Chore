"""
Unit tests for the centralized Transaction service.

Tests verify that each factory function creates the correct Transaction
record type with proper field values, and that cleanup helpers work.
"""
import pytest
from datetime import datetime, timezone
from backend.services.transaction_service import (
    record_earn,
    record_redeem,
    record_penalty,
    detach_instance_references,
    delete_user_transactions,
)
from backend import models


@pytest.fixture
def test_user(db_session, seeded_db):
    """A user for transaction tests."""
    user = models.User(
        nickname="TxTestUser", login_pin="1234", role_id=1,
        current_points=100, lifetime_points=500,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_task_instance(db_session, seeded_db, test_user):
    """A task + instance for reference_instance_id tests."""
    task = models.Task(
        name="TxTask", description="test", default_due_time="12:00",
        base_points=50, schedule_type="one_off",
    )
    db_session.add(task)
    db_session.commit()

    instance = models.TaskInstance(
        task_id=task.id, user_id=test_user.id, status="PENDING",
        due_time=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
    )
    db_session.add(instance)
    db_session.commit()
    return instance


# ─── record_earn ───────────────────────────────────────────────────

class TestRecordEarn:
    def test_creates_earn_transaction(self, db_session, test_user, test_task_instance):
        now = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
        txn = record_earn(
            db_session,
            user_id=test_user.id,
            base_points=50,
            multiplier=1.5,
            awarded_points=80,
            description="Completed task: TxTask (+5 Daily Bonus)",
            reference_instance_id=test_task_instance.id,
            timestamp=now,
        )
        db_session.commit()

        assert txn.id is not None
        assert txn.type == "EARN"
        assert txn.user_id == test_user.id
        assert txn.base_points_value == 50
        assert txn.multiplier_used == 1.5
        assert txn.awarded_points == 80
        assert txn.description == "Completed task: TxTask (+5 Daily Bonus)"
        assert txn.reference_instance_id == test_task_instance.id
        # SQLite strips tzinfo, so compare naive values
        assert txn.timestamp.replace(tzinfo=None) == now.replace(tzinfo=None)

    def test_earn_without_instance_reference(self, db_session, test_user):
        now = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
        txn = record_earn(
            db_session,
            user_id=test_user.id,
            base_points=10,
            multiplier=1.0,
            awarded_points=10,
            description="Bonus points",
            reference_instance_id=None,
            timestamp=now,
        )
        db_session.commit()

        assert txn.reference_instance_id is None
        assert txn.type == "EARN"

    def test_does_not_auto_commit(self, db_session, test_user):
        """Verify the function adds to session but does NOT commit."""
        now = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
        record_earn(
            db_session, user_id=test_user.id, base_points=10,
            multiplier=1.0, awarded_points=10, description="test",
            reference_instance_id=None, timestamp=now,
        )
        # Before commit, the ID should be None (not flushed)
        # After rollback, transaction should not persist
        db_session.rollback()
        result = db_session.query(models.Transaction).filter(
            models.Transaction.description == "test"
        ).first()
        assert result is None


# ─── record_redeem ─────────────────────────────────────────────────

class TestRecordRedeem:
    def test_creates_redeem_transaction(self, db_session, test_user):
        now = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
        txn = record_redeem(
            db_session,
            user_id=test_user.id,
            cost_points=75,
            description="Redeemed reward: Ice Cream",
            timestamp=now,
        )
        db_session.commit()

        assert txn.type == "REDEEM"
        assert txn.base_points_value == 75
        assert txn.multiplier_used == 1.0
        assert txn.awarded_points == -75  # Negative for spend
        assert txn.description == "Redeemed reward: Ice Cream"

    def test_redeem_split_with_description(self, db_session, test_user):
        now = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
        txn = record_redeem(
            db_session,
            user_id=test_user.id,
            cost_points=30,
            description="Redeemed reward: Movie Night (Split)",
            timestamp=now,
        )
        db_session.commit()

        assert txn.awarded_points == -30
        assert "(Split)" in txn.description


# ─── record_penalty ────────────────────────────────────────────────

class TestRecordPenalty:
    def test_creates_penalty_transaction(self, db_session, test_user):
        now = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
        txn = record_penalty(
            db_session,
            user_id=test_user.id,
            points=20,
            reason="Misbehaved at dinner",
            timestamp=now,
        )
        db_session.commit()

        assert txn.type == "PENALTY"
        assert txn.base_points_value == 20
        assert txn.multiplier_used == 1.0
        assert txn.awarded_points == -20
        assert txn.description == "Misbehaved at dinner"
        assert txn.reference_instance_id is None


# ─── detach_instance_references ────────────────────────────────────

class TestDetachInstanceReferences:
    def test_nulls_out_references(self, db_session, test_user, test_task_instance):
        now = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
        txn = record_earn(
            db_session, user_id=test_user.id, base_points=10,
            multiplier=1.0, awarded_points=10, description="ref test",
            reference_instance_id=test_task_instance.id, timestamp=now,
        )
        db_session.commit()
        assert txn.reference_instance_id == test_task_instance.id

        count = detach_instance_references(db_session, [test_task_instance.id])
        db_session.commit()

        db_session.refresh(txn)
        assert txn.reference_instance_id is None
        assert count == 1

    def test_empty_list_returns_zero(self, db_session):
        count = detach_instance_references(db_session, [])
        assert count == 0

    def test_no_matching_ids_returns_zero(self, db_session):
        count = detach_instance_references(db_session, [99999])
        assert count == 0


# ─── delete_user_transactions ──────────────────────────────────────

class TestDeleteUserTransactions:
    def test_deletes_all_user_transactions(self, db_session, test_user):
        now = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
        record_earn(db_session, user_id=test_user.id, base_points=10,
                    multiplier=1.0, awarded_points=10, description="t1",
                    reference_instance_id=None, timestamp=now)
        record_penalty(db_session, user_id=test_user.id, points=5,
                       reason="t2", timestamp=now)
        db_session.commit()

        remaining = db_session.query(models.Transaction).filter(
            models.Transaction.user_id == test_user.id).count()
        assert remaining == 2

        count = delete_user_transactions(db_session, test_user.id)
        db_session.commit()

        remaining = db_session.query(models.Transaction).filter(
            models.Transaction.user_id == test_user.id).count()
        assert remaining == 0
        assert count == 2

    def test_does_not_affect_other_users(self, db_session, seeded_db):
        user_a = models.User(nickname="UserA", login_pin="1111", role_id=1)
        user_b = models.User(nickname="UserB", login_pin="2222", role_id=1)
        db_session.add_all([user_a, user_b])
        db_session.commit()

        now = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
        record_earn(db_session, user_id=user_a.id, base_points=10,
                    multiplier=1.0, awarded_points=10, description="a",
                    reference_instance_id=None, timestamp=now)
        record_earn(db_session, user_id=user_b.id, base_points=10,
                    multiplier=1.0, awarded_points=10, description="b",
                    reference_instance_id=None, timestamp=now)
        db_session.commit()

        delete_user_transactions(db_session, user_a.id)
        db_session.commit()

        assert db_session.query(models.Transaction).filter(
            models.Transaction.user_id == user_a.id).count() == 0
        assert db_session.query(models.Transaction).filter(
            models.Transaction.user_id == user_b.id).count() == 1
