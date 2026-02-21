"""
Pytest configuration and shared fixtures for ChoreSpec tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.main import app, get_db
from backend import models

# Use in-memory SQLite for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def seeded_db(db_session):
    """Database with default roles seeded."""
    roles = [
        models.Role(name="Admin", multiplier_value=1.0),
        models.Role(name="Contributor", multiplier_value=1.0),
        models.Role(name="Teenager", multiplier_value=1.2),
        models.Role(name="Child", multiplier_value=1.5),
    ]
    for role in roles:
        db_session.add(role)
    db_session.commit()
    return db_session


@pytest.fixture
def admin_user(seeded_db):
    """Create an admin user for testing."""
    admin_role = seeded_db.query(models.Role).filter(
        models.Role.name == "Admin").first()
    user = models.User(
        nickname="TestAdmin",
        login_pin="1234",
        role_id=admin_role.id,
        current_points=0,
        lifetime_points=0
    )
    seeded_db.add(user)
    seeded_db.commit()
    seeded_db.refresh(user)
    return user


# BDD context storage
@pytest.fixture
def context():
    """Shared context for BDD step definitions."""
    return {}
