"""
Test configuration and shared fixtures.

This sets up a test database using SQLite in memory instead of PostgreSQL.
Why? Because tests should be fast and not depend on external services.
You don't want to need a running PostgreSQL just to run your tests.

SQLite in-memory means the database only exists while the test runs
and disappears afterwards — no cleanup needed.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# SQLite in-memory database for testing — faster than PostgreSQL
# and doesn't require any setup
TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Replace the real database session with our test session."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Tell FastAPI to use the test database instead of the real one
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test and drop them after.

    autouse=True means this runs automatically for every test
    without needing to explicitly request it. This ensures each
    test starts with a clean database.
    """
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    """Provide a test HTTP client for making requests to the API."""
    return TestClient(app)


@pytest.fixture
def sample_user_data():
    """Provide sample user data for tests."""
    return {
        "keycloak_id": "kc-test-user-001",
        "email": "test@example.com",
        "full_name": "Test User",
        "phone": "+45 12345678",
        "default_address": "Test Street 1, 2100 Copenhagen",
    }
