
from datetime import datetime, timedelta
from backend import crud, models


def test_get_user_transactions(db_session, seeded_db):
    role = db_session.query(models.Role).first()
    user = models.User(nickname="TxCRUDUser",
                       login_pin="1111", role_id=role.id)
    db_session.add(user)
    db_session.commit()

    # Create transactions
    t1 = models.Transaction(
        user_id=user.id, type="EARN", base_points_value=10,
        multiplier_used=1, awarded_points=10, timestamp=datetime.now()
    )
    t2 = models.Transaction(
        user_id=user.id, type="REDEEM", base_points_value=0,
        multiplier_used=1, awarded_points=-5, timestamp=datetime.now()
    )
    db_session.add_all([t1, t2])
    db_session.commit()

    # Get all
    txs = crud.get_user_transactions(db_session, user.id)
    assert len(txs) == 2

    # Filter by type
    txs_earn = crud.get_user_transactions(db_session, user.id, type="EARN")
    assert len(txs_earn) == 1
    assert txs_earn[0].type == "EARN"

    # Filter by date (future)
    future = datetime.now() + timedelta(days=1)
    txs_future = crud.get_user_transactions(
        db_session, user.id, start_date=future)
    assert len(txs_future) == 0


def test_get_all_transactions(db_session, seeded_db):
    # Setup multiple users
    role = db_session.query(models.Role).first()
    u1 = models.User(nickname="U1", login_pin="1", role_id=role.id)
    u2 = models.User(nickname="U2", login_pin="1", role_id=role.id)
    db_session.add_all([u1, u2])
    db_session.commit()

    t1 = models.Transaction(
        user_id=u1.id, type="EARN", base_points_value=10, multiplier_used=1,
        awarded_points=10, timestamp=datetime.now()
    )
    t2 = models.Transaction(
        user_id=u2.id, type="EARN", base_points_value=10, multiplier_used=1,
        awarded_points=10, timestamp=datetime.now()
    )
    db_session.add_all([t1, t2])
    db_session.commit()

    # Get all
    txs = crud.get_all_transactions(db_session)
    # seeded_db might have transactions? + composed ones
    assert len(txs) >= 2

    # Filter by user
    txs_u1 = crud.get_all_transactions(db_session, user_id=u1.id)
    assert len(txs_u1) == 1
    assert txs_u1[0].user_id == u1.id

    # Filter by search
    # Add one with specific title if possible? Transaction doesn't have title/desc in model?
    # Checking model...
    # Model has description

    t3 = models.Transaction(
        user_id=u1.id, type="EARN", base_points_value=10, multiplier_used=1,
        awarded_points=10, timestamp=datetime.now(), description="UniqueTaskName"
    )
    db_session.add(t3)
    db_session.commit()

    txs_search = crud.get_all_transactions(db_session, search="Unique")
    assert len(txs_search) == 1
    assert txs_search[0].description == "UniqueTaskName"
