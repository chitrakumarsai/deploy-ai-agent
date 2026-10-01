"""Chat API: API-key auth on chat endpoints, and /recent/ returning the newest messages.

Runs against in-memory SQLite (no Postgres needed), from the repo root:
    uv run --no-project --with fastapi --with sqlmodel --with httpx2 --with pytest pytest backend/tests -q
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
os.environ.setdefault("DATABASE_URL", "sqlite://")  # db.py builds its engine at import time
os.environ.setdefault("API_KEY", "import-time-key")  # main.py refuses to start without one

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402

from api.chat.models import ChatMessage, get_utc_now  # noqa: E402
from api.db import get_session  # noqa: E402
from main import app  # noqa: E402

KEY = "test-key-123"


@pytest.fixture
def engine(monkeypatch):
    monkeypatch.setenv("API_KEY", KEY)
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                           poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = session_override
    yield engine
    app.dependency_overrides.clear()


@pytest.fixture
def client(engine):
    return TestClient(app)


AUTH = {"X-API-Key": KEY}


@pytest.mark.parametrize(("method", "path"), [("get", "/api/chats/recent/"), ("post", "/api/chats/")])
@pytest.mark.parametrize("headers", [{}, {"X-API-Key": "wrong"}])
def test_chat_endpoints_reject_missing_or_wrong_api_key(client, method, path, headers):
    body = {"json": {"message": "hi"}} if method == "post" else {}
    response = client.request(method.upper(), path, headers=headers, **body)

    assert response.status_code == 401


def test_chat_endpoints_fail_closed_when_no_api_key_is_configured(client, monkeypatch):
    monkeypatch.delenv("API_KEY")

    assert client.get("/api/chats/recent/", headers=AUTH).status_code == 503


def test_health_and_index_stay_public(client):
    assert client.get("/api/chats/").status_code == 200
    assert client.get("/").status_code == 200


def test_creating_a_message_stores_a_utc_timestamp(client):
    before = datetime.now(timezone.utc)

    response = client.post("/api/chats/", headers=AUTH, json={"message": "hello"})

    assert response.status_code == 200
    created = datetime.fromisoformat(response.json()["created_at"])
    created = created if created.tzinfo else created.replace(tzinfo=timezone.utc)
    assert abs(created - before) < timedelta(seconds=5)


def test_get_utc_now_is_the_real_utc_time():
    assert abs(get_utc_now() - datetime.now(timezone.utc)) < timedelta(seconds=5)


def test_recent_returns_the_ten_newest_messages_newest_first(client, engine):
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    with Session(engine) as session:
        for minute in range(12):  # inserted oldest-first
            session.add(ChatMessage(message=f"m{minute}", created_at=start + timedelta(minutes=minute)))
        session.commit()

    response = client.get("/api/chats/recent/", headers=AUTH)

    assert response.status_code == 200
    assert [item["message"] for item in response.json()] == [f"m{n}" for n in range(11, 1, -1)]
