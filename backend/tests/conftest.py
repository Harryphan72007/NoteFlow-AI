from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.database import Base, engine
from backend.app.main import app


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    client = TestClient(app)
    login = client.post("/api/auth/login", json={"username": "local.user", "password": "noteflow-local"})
    assert login.status_code == 200, login.text
    client.headers.update({"Authorization": f"Bearer {login.json()['access_token']}"})
    return client
