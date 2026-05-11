"""Test setup.
Tests use SQLite instead of MySQL.
A new empty database is created for each test so tests do not interfere with each other.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models import User  # noqa: F401 — registers User in Base.metadata
from main import app


@pytest.fixture
def client():
    """ Client that sends requests to the app using SQLite"""

    # Create a new database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Make sure the users table exists
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    def override_get_db():
        # Open a connection to temporary database
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    # Change MySQL to SQLite for this testing.
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

    # Change to real database connection after the test finished
    app.dependency_overrides.clear()