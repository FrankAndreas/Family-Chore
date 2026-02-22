

from backend import models
from datetime import datetime


def test_get_user_transactions_api(client, db_session, seeded_db):
    # Setup User and Transaction
    role = db_session.query(models.Role).first()
    u = models.User(nickname="TxUserAPI", login_pin="1", role_id=role.id)
    db_session.add(u)
    db_session.commit()

    t = models.Transaction(
        user_id=u.id,
        type="EARN",
        base_points_value=10,
        multiplier_used=1,
        awarded_points=10,
        timestamp=datetime.now()
    )
    db_session.add(t)
    db_session.commit()

    # Get
    resp = client.get(f"/users/{u.id}/transactions")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["type"] == "EARN"

    # Filter by type
    resp_filter = client.get(f"/users/{u.id}/transactions?txn_type=REDEEM")
    assert len(resp_filter.json()) == 0


def test_get_all_transactions_api(client, db_session, seeded_db):
    resp = client.get("/transactions")
    # Should get the one from previous test + whatever else
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

    # Filter by user
    role = db_session.query(models.Role).first()
    u = models.User(nickname="GlobalTxUser", login_pin="1", role_id=role.id)
    db_session.add(u)
    db_session.commit()
    t = models.Transaction(
        user_id=u.id,
        type="EARN",
        base_points_value=5,
        multiplier_used=1,
        awarded_points=5,
        timestamp=datetime.now()
    )
    db_session.add(t)
    db_session.commit()

    resp_user = client.get(f"/transactions?user_id={u.id}")
    assert len(resp_user.json()) == 1
