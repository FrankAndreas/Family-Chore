
"""
Unit tests for Transaction operations.
"""
from datetime import datetime, timedelta, timezone
from backend import crud, models


class TestTransactionHistory:
    """Test transaction history retrieval."""

    def test_get_user_transactions_returns_correct_history(self, seeded_db):
        """Test fetching transactions for a specific user."""
        # Arrange
        child_role = seeded_db.query(models.Role).filter(
            models.Role.name == "Child"
        ).first()

        user = models.User(
            nickname="HistoryUser",
            login_pin="1234",
            role_id=child_role.id,
            current_points=0,
            lifetime_points=0
        )
        seeded_db.add(user)
        seeded_db.commit()

        # Create some transactions
        # 1. Earn transaction
        t1 = models.Transaction(
            user_id=user.id,
            type="EARN",
            base_points_value=10,
            multiplier_used=1.0,
            awarded_points=10,
            timestamp=datetime.now(timezone.utc) - timedelta(hours=2),
            description="Task A"
        )
        # 2. Redeem transaction
        t2 = models.Transaction(
            user_id=user.id,
            type="REDEEM",
            base_points_value=20,
            multiplier_used=1.0,
            awarded_points=-5,
            timestamp=datetime.now(timezone.utc) - timedelta(hours=1),
            description="Reward B"
        )

        seeded_db.add(t1)
        seeded_db.add(t2)
        seeded_db.commit()

        # Act
        transactions = crud.get_user_transactions(seeded_db, user.id)

        # Assert
        assert len(transactions) == 2
        # Should be ordered by timestamp desc
        assert transactions[0].id == t2.id
        assert transactions[1].id == t1.id
        assert transactions[0].type == "REDEEM"
        assert transactions[1].type == "EARN"

    def test_get_all_transactions_returns_global_history(self, seeded_db):
        """Test fetching global transaction history."""
        # Arrange
        child_role = seeded_db.query(models.Role).filter(
            models.Role.name == "Child"
        ).first()

        user1 = models.User(
            nickname="User1", login_pin="1111", role_id=child_role.id)
        user2 = models.User(
            nickname="User2", login_pin="2222", role_id=child_role.id)
        seeded_db.add_all([user1, user2])
        seeded_db.commit()

        # Create transactions for both users
        t1 = models.Transaction(
            user_id=user1.id,
            type="EARN",
            base_points_value=10,
            multiplier_used=1.0,
            awarded_points=10,
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=10),
            description="Task 1"
        )
        t2 = models.Transaction(
            user_id=user2.id,
            type="EARN",
            base_points_value=20,
            multiplier_used=1.0,
            awarded_points=20,
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=5),
            description="Task 2"
        )

        seeded_db.add(t1)
        seeded_db.add(t2)
        seeded_db.commit()

        # Act
        transactions = crud.get_all_transactions(seeded_db)

        # Assert
        ids = [t.id for t in transactions]
        assert t1.id in ids
        assert t2.id in ids

    def test_pagination_works(self, seeded_db):
        """Test pagination for transactions."""
        # Arrange
        child_role = seeded_db.query(models.Role).filter(
            models.Role.name == "Child"
        ).first()
        user = models.User(nickname="PageUser",
                           login_pin="1234", role_id=child_role.id)
        seeded_db.add(user)
        seeded_db.commit()

        # Create 15 transactions
        for i in range(15):
            t = models.Transaction(
                user_id=user.id,
                type="EARN",
                base_points_value=10,
                multiplier_used=1.0,
                awarded_points=10,
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=i),
                description=f"Task {i}"
            )
            seeded_db.add(t)
        seeded_db.commit()

        # Act
        page1 = crud.get_user_transactions(
            seeded_db, user.id, skip=0, limit=10)
        page2 = crud.get_user_transactions(
            seeded_db, user.id, skip=10, limit=10)

        # Assert
        assert len(page1) == 10
        assert len(page2) == 5

    def test_filtering_transactions(self, seeded_db):
        """Test filtering by type, search, and date."""
        # Arrange
        child_role = seeded_db.query(models.Role).filter(
            models.Role.name == "Child").first()
        user = models.User(nickname="FilterUser",
                           login_pin="1234", role_id=child_role.id)
        seeded_db.add(user)
        seeded_db.commit()

        # 1. Earn Task A (Yesterday)
        t1 = models.Transaction(
            user_id=user.id, type="EARN", base_points_value=10, multiplier_used=1.0,
            awarded_points=10, timestamp=datetime.now(timezone.utc) - timedelta(days=1), description="Clean Room"
        )
        # 2. Redeem Reward B (Today)
        t2 = models.Transaction(
            user_id=user.id, type="REDEEM", base_points_value=50, multiplier_used=1.0,
            awarded_points=-50, timestamp=datetime.now(timezone.utc), description="Ice Cream"
        )

        seeded_db.add_all([t1, t2])
        seeded_db.commit()

        # Act & Assert

        # Filter by Type
        earn_txs = crud.get_user_transactions(seeded_db, user.id, type="EARN")
        assert len(earn_txs) == 1
        assert earn_txs[0].description == "Clean Room"

        redeem_txs = crud.get_user_transactions(
            seeded_db, user.id, type="REDEEM")
        assert len(redeem_txs) == 1
        assert redeem_txs[0].description == "Ice Cream"

        # Filter by Search
        search_txs = crud.get_user_transactions(
            seeded_db, user.id, search="Ice")
        assert len(search_txs) == 1
        assert search_txs[0].description == "Ice Cream"

        search_fail = crud.get_user_transactions(
            seeded_db, user.id, search="Pizza")
        assert len(search_fail) == 0

        # Filter by User (Global)
        global_user_txs = crud.get_all_transactions(seeded_db, user_id=user.id)
        assert len(global_user_txs) == 2
