from fastapi.testclient import TestClient
from backend.main import app
from backend import models
from backend.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.pool import StaticPool
engine = create_engine("sqlite:///:memory:", poolclass=StaticPool, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Create role and user manually
db = TestingSessionLocal()
role = models.Role(name="Admin", multiplier_value=1.0)
db.add(role)
db.commit()
db.refresh(role)

from backend.security import get_password_hash
user = models.User(nickname="E2ETest", login_pin=get_password_hash("1234"), role_id=role.id, current_points=0, lifetime_points=0)
db.add(user)
db.commit()

# Login
resp = client.post("/login/", json={"nickname": "E2ETest", "login_pin": "1234"})
assert resp.status_code == 200, resp.text
token = resp.json()["access_token"]

# Hit a protected endpoint
resp = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
assert resp.status_code == 200, resp.text

# Hit an admin-only endpoint
resp = client.post("/roles/", headers={"Authorization": f"Bearer {token}"}, json={"name": "NewRule", "multiplier_value": 1.2})
assert resp.status_code == 200, resp.text
print("JWT E2E SUCCESS")
