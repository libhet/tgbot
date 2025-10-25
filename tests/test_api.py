from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import app
from app.config import Settings, get_settings
from app.database import Base, get_db


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def override_get_settings() -> Settings:
        return Settings(default_intervals=[1, 3, 7], database_url="sqlite+pysqlite:///:memory:")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = override_get_settings

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_schedule_flow(client: TestClient):
    create_payload = {
        "title": "Новая карточка",
        "description": "Описание",
        "start_at": "2024-01-01T00:00:00",
        "intervals": [1, 3, 7],
    }
    response = client.post("/schedules", json=create_payload)
    assert response.status_code == 201
    schedule = response.json()
    schedule_id = schedule["id"]

    first_review = datetime.fromisoformat(schedule["next_review_at"])
    assert first_review == datetime(2024, 1, 2, 0, 0, 0)

    history_response = client.post(
        f"/schedules/{schedule_id}/history",
        json={"success": True, "reviewed_at": schedule["next_review_at"]},
    )
    assert history_response.status_code == 200
    schedule_after_success = history_response.json()
    assert schedule_after_success["interval_index"] == 1

    postpone_to = datetime.fromisoformat(schedule_after_success["next_review_at"]) + timedelta(days=2)
    postpone_response = client.post(
        f"/schedules/{schedule_id}/reschedule",
        json={"next_review_at": postpone_to.isoformat()},
    )
    assert postpone_response.status_code == 200
    assert postpone_response.json()["next_review_at"] == postpone_to.isoformat()

    history_list = client.get(f"/schedules/{schedule_id}/history")
    assert history_list.status_code == 200
    assert len(history_list.json()) == 1

    delete_response = client.delete(f"/schedules/{schedule_id}")
    assert delete_response.status_code == 204

    schedules_after_cancel = client.get("/schedules").json()
    assert schedules_after_cancel == []

    inactive_list = client.get("/schedules", params={"active": False}).json()
    assert inactive_list[0]["active"] is False
