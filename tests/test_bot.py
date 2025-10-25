from __future__ import annotations

import pytest

from datetime import date

from app import schemas
from bot import handlers, views


@pytest.fixture()
def sample_exercises() -> list[schemas.ExerciseRead]:
    return [
        schemas.ExerciseRead(
            id=1,
            title="Test Exercise",
            description="Description",
            type="warmup",
            status="published",
            sessions=[
                schemas.PracticeSessionRead(
                    id=1,
                    exercise_id=1,
                    date=date(2024, 1, 1),
                    status="planned",
                    exercise_title="Test Exercise",
                )
            ],
        )
    ]


@pytest.fixture()
def sample_calendar() -> list[schemas.CalendarDay]:
    return [
        schemas.CalendarDay(
            date=date(2024, 1, 1),
            sessions=[
                schemas.PracticeSessionRead(
                    id=1,
                    exercise_id=1,
                    date=date(2024, 1, 1),
                    status="planned",
                    exercise_title="Test Exercise",
                )
            ],
        )
    ]


def test_render_exercise_list(sample_exercises) -> None:
    text = views.render_exercise_list(sample_exercises)
    assert "Список упражнений" in text
    assert "Test Exercise" in text


def test_render_calendar_view(sample_calendar) -> None:
    text = views.render_calendar_view(sample_calendar)
    assert "Ближайшие практики" in text
    assert "2024" in text
    assert "Test Exercise" in text


@pytest.mark.asyncio()
async def test_send_list_view(monkeypatch, sample_exercises, sample_calendar) -> None:
    class FakeMessage:
        def __init__(self) -> None:
            self.payloads = []

        async def answer(self, text, reply_markup=None, parse_mode=None):
            self.payloads.append((text, reply_markup, parse_mode))

    fake_message = FakeMessage()

    monkeypatch.setattr(handlers, "fetch_data", lambda: (sample_exercises, sample_calendar))

    await handlers.send_list_view(fake_message)

    assert fake_message.payloads
    text, markup, parse_mode = fake_message.payloads[0]
    assert "Список упражнений" in text
    assert parse_mode == "HTML"
    assert any(button.text.startswith("📋") for row in markup.inline_keyboard for button in row)


@pytest.mark.asyncio()
async def test_send_calendar_view_via_callback(monkeypatch, sample_exercises, sample_calendar) -> None:
    class FakeEditMessage:
        def __init__(self) -> None:
            self.edits = []

        async def edit_text(self, text, reply_markup=None, parse_mode=None):
            self.edits.append((text, reply_markup, parse_mode))

    class FakeCallback:
        def __init__(self) -> None:
            self.message = FakeEditMessage()
            self.answered = False
            self.data = handlers.ViewCallback.data(handlers.VIEW_CALENDAR)

        async def answer(self, *args, **kwargs):
            self.answered = True

    fake_callback = FakeCallback()
    monkeypatch.setattr(handlers, "fetch_data", lambda: (sample_exercises, sample_calendar))

    await handlers.send_calendar_view(fake_callback)

    assert fake_callback.answered
    assert fake_callback.message.edits
    text, markup, parse_mode = fake_callback.message.edits[0]
    assert "Ближайшие практики" in text
    assert "Test Exercise" in text
    assert parse_mode == "HTML"
    assert any(button.text.startswith("📅") for row in markup.inline_keyboard for button in row)


def test_view_callback_parse() -> None:
    data = handlers.ViewCallback.data(handlers.VIEW_LIST)
    assert handlers.ViewCallback.parse(data) == handlers.VIEW_LIST
    assert handlers.ViewCallback.parse("unknown") is None
