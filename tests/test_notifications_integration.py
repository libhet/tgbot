from datetime import datetime, time, timedelta
import time as time_module

import pytest

from tgbot.models import NotificationSettings, Reminder
from tgbot.notifications import InMemoryNotificationSettingsProvider, NotificationService
from tgbot.repository import InMemoryReminderRepository
from tgbot.scheduler import ReminderScheduler
from tgbot.telegram import TelegramAPIClient


class FakeHTTPClient:
    def __init__(self) -> None:
        self.requests = []

    def post_json(self, url, payload, timeout=None):  # pragma: no cover - trivial wrapper
        self.requests.append({"url": url, "payload": payload})
        return {"ok": True, "result": {"url": url}}


@pytest.fixture()
def notification_setup():
    repository = InMemoryReminderRepository()
    settings = NotificationSettings(
        user_id=1,
        frequency=timedelta(hours=6),
        quiet_hours_start=time(22, 0),
        quiet_hours_end=time(7, 0),
    )
    settings_provider = InMemoryNotificationSettingsProvider([settings])
    http = FakeHTTPClient()
    telegram = TelegramAPIClient("token", http_client=http)
    service = NotificationService(repository, telegram, settings_provider)
    reminder = Reminder(
        reminder_id="rem-1",
        user_id=1,
        chat_id=100,
        message="Пора повторить упражнения",
        scheduled_at=datetime(2023, 1, 1, 21, 0),
    )
    service.add_reminder(reminder)
    return repository, settings_provider, http, service, reminder


def test_quiet_hours_prevents_sending(notification_setup):
    repository, settings_provider, http, service, reminder = notification_setup
    now = datetime(2023, 1, 1, 23, 0)

    service.send_due_reminders(now)

    assert http.requests == []
    stored = repository.get(reminder.reminder_id)
    assert stored.scheduled_at == datetime(2023, 1, 2, 7, 0)


def test_send_due_notification_with_inline_keyboard(notification_setup):
    repository, settings_provider, http, service, reminder = notification_setup
    now = datetime(2023, 1, 2, 10, 0)
    # ensure reminder is due
    repository.get(reminder.reminder_id).scheduled_at = now - timedelta(minutes=1)

    service.send_due_reminders(now)

    assert len(http.requests) == 1
    request_payload = http.requests[0]["payload"]
    assert request_payload["chat_id"] == reminder.chat_id
    assert "inline_keyboard" in request_payload["reply_markup"]
    buttons = request_payload["reply_markup"]["inline_keyboard"]
    assert any(button[0]["callback_data"].startswith("snooze:") for button in buttons)
    assert any(button[0]["callback_data"].startswith("reschedule:") for button in buttons)

    stored = repository.get(reminder.reminder_id)
    assert stored.scheduled_at == now + settings_provider.get_settings(reminder.user_id).frequency


def test_handle_snooze_callback(notification_setup):
    repository, settings_provider, http, service, reminder = notification_setup
    now = datetime(2023, 1, 2, 10, 0)

    service.handle_callback("cbq", f"snooze:{reminder.reminder_id}:900", now=now)

    stored = repository.get(reminder.reminder_id)
    assert stored.scheduled_at == now + timedelta(seconds=900)
    assert http.requests[-1]["url"].endswith("answerCallbackQuery")


def test_scheduler_runs(notification_setup):
    repository, settings_provider, http, service, reminder = notification_setup
    now = datetime(2023, 1, 2, 9, 0)
    repository.get(reminder.reminder_id).scheduled_at = now - timedelta(minutes=1)
    calls = []

    original_send = service.send_due_reminders

    def wrapped(moment):
        calls.append(moment)
        return original_send(moment)

    service.send_due_reminders = wrapped  # type: ignore[assignment]

    scheduler = ReminderScheduler(service, poll_interval=timedelta(milliseconds=50), now_func=lambda: now)
    scheduler.start()
    time_module.sleep(0.12)
    scheduler.stop()

    assert calls, "Scheduler did not execute send_due_reminders"
    assert any(req["url"].endswith("sendMessage") for req in http.requests)
