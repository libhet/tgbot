from __future__ import annotations

from datetime import date, timedelta


def test_get_exercises_returns_data(client) -> None:
    response = client.get("/api/exercises")
    assert response.status_code == 200
    payload = response.json()
    titles = {item["title"] for item in payload}
    assert "Breathing Control" in titles
    assert any(item["sessions"] for item in payload)
    assert any(session.get("exercise_title") for item in payload for session in item["sessions"])


def test_filter_exercises_by_type(client) -> None:
    response = client.get("/api/exercises", params={"exercise_type": "technique"})
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "Chromatic Scales"
    assert all(session["exercise_id"] == payload[0]["id"] for session in payload[0]["sessions"])


def test_calendar_status_filter(client) -> None:
    response = client.get("/api/calendar", params={"status": "completed"})
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert all(session["status"] == "completed" for day in payload for session in day["sessions"])
    assert all(session.get("exercise_title") for day in payload for session in day["sessions"])


def test_calendar_date_range(client) -> None:
    today = date.today()
    next_month = today + timedelta(days=31)
    response = client.get(
        "/api/calendar",
        params={"date_from": today.isoformat(), "date_to": next_month.isoformat()},
    )
    assert response.status_code == 200
    payload = response.json()
    assert all(today <= date.fromisoformat(day["date"]) <= next_month for day in payload)
