import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    """Fresh in-memory SQLite DB for every single test, so tests never leak
    state into each other and never touch your real data. StaticPool is
    required here: without it, each new session would get its own separate
    (and empty) in-memory database instead of sharing the one this test set up."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    """Signs up a fresh shop and returns headers ready to use on protected
    endpoints, plus the client, for tests that need an authenticated shop."""
    r = client.post(
        "/auth/signup",
        json={"shop_name": "Test Boutique", "email": "owner@test.com", "password": "secret123"},
    )
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """The login rate limiter is a process-wide in-memory store, so it has
    to be cleared between tests or one test's failed logins would bleed
    into the next test's lockout state."""
    from app.rate_limit import _reset_all_for_tests
    _reset_all_for_tests()
    yield
    _reset_all_for_tests()
