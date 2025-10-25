"""Notification orchestration logic."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Optional, Protocol

from .models import NotificationSettings, Reminder
from .repository import ReminderRepository
from .telegram import TelegramAPIClient


class NotificationSettingsProvider(Protocol):
    """Returns per-user notification preferences."""

    def get_settings(self, user_id: int) -> NotificationSettings:
        ...


class InMemoryNotificationSettingsProvider:
    """Simple settings store used in tests."""

    def __init__(self, settings: Optional[Iterable[NotificationSettings]] = None) -> None:
        self._store: Dict[int, NotificationSettings] = {}
        if settings:
            for pref in settings:
                self._store[pref.user_id] = pref

    def get_settings(self, user_id: int) -> NotificationSettings:
        if user_id not in self._store:
            self._store[user_id] = NotificationSettings(user_id=user_id)
        return self._store[user_id]

    def upsert(self, settings: NotificationSettings) -> None:
        self._store[settings.user_id] = settings


class NotificationService:
    """High-level service that schedules and sends notifications."""

    def __init__(
        self,
        repository: ReminderRepository,
        telegram_client: TelegramAPIClient,
        settings_provider: NotificationSettingsProvider,
        snooze_options: Optional[Iterable[timedelta]] = None,
    ) -> None:
        self._repository = repository
        self._telegram = telegram_client
        self._settings_provider = settings_provider
        self._snooze_options: List[timedelta] = list(snooze_options) if snooze_options else [
            timedelta(minutes=15),
            timedelta(hours=1),
        ]

    def _build_keyboard(self, reminder: Reminder) -> Dict[str, List[List[Dict[str, str]]]]:
        rows: List[List[Dict[str, str]]] = []
        for option in self._snooze_options:
            seconds = int(option.total_seconds())
            text = self._format_snooze_label(option)
            rows.append([
                {
                    "text": text,
                    "callback_data": f"snooze:{reminder.reminder_id}:{seconds}",
                }
            ])
        rows.append(
            [
                {
                    "text": "Перенести на завтра",
                    "callback_data": f"reschedule:{reminder.reminder_id}:tomorrow",
                }
            ]
        )
        return {"inline_keyboard": rows}

    @staticmethod
    def _format_snooze_label(delta: timedelta) -> str:
        minutes = int(delta.total_seconds() // 60)
        if minutes < 60:
            return f"Отложить на {minutes} мин"
        hours = minutes // 60
        return f"Отложить на {hours} ч"

    def send_due_reminders(self, now: Optional[datetime] = None) -> None:
        moment = now or datetime.utcnow()
        due = list(self._repository.list_due(moment))
        for reminder in due:
            settings = self._settings_provider.get_settings(reminder.user_id)
            if settings.is_quiet_time(moment):
                reminder.postpone(self._next_allowed_time(moment, settings))
                self._repository.update(reminder)
                continue
            keyboard = self._build_keyboard(reminder)
            reminder.reply_markup = keyboard
            self._telegram.send_message(reminder.chat_id, reminder.message, reply_markup=keyboard)
            next_time = moment + settings.frequency
            reminder.postpone(next_time)
            self._repository.update(reminder)

    def _next_allowed_time(self, now: datetime, settings: NotificationSettings) -> datetime:
        quiet_start = settings.quiet_hours_start
        quiet_end = settings.quiet_hours_end
        if quiet_start is None or quiet_end is None:
            return now

        if quiet_start < quiet_end:
            candidate = datetime.combine(now.date(), quiet_end)
            if candidate <= now:
                candidate = candidate + timedelta(days=1)
            return candidate

        # Quiet hours wrap midnight
        if now.time() < quiet_end:
            return datetime.combine(now.date(), quiet_end)
        candidate = datetime.combine(now.date() + timedelta(days=1), quiet_end)
        return candidate

    def handle_callback(self, callback_query_id: str, data: str, now: Optional[datetime] = None) -> None:
        moment = now or datetime.utcnow()
        action, reminder_id, *rest = data.split(":")
        reminder = self._repository.get(reminder_id)
        settings = self._settings_provider.get_settings(reminder.user_id)

        if action == "snooze":
            seconds = int(rest[0]) if rest else int(settings.frequency.total_seconds())
            reminder.postpone(moment + timedelta(seconds=seconds))
            self._telegram.answer_callback(callback_query_id, text="Напоминание отложено")
        elif action == "reschedule":
            when = rest[0] if rest else "tomorrow"
            if when == "tomorrow":
                target = (moment + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
            else:
                target = datetime.fromisoformat(when)
            reminder.postpone(target)
            self._telegram.answer_callback(callback_query_id, text="Перенос выполнен")
        else:
            self._telegram.answer_callback(callback_query_id, text="Неизвестное действие")
            return

        self._repository.update(reminder)

    def add_reminder(self, reminder: Reminder) -> None:
        """Persist a new reminder and attach default inline keyboard."""

        reminder.reply_markup = self._build_keyboard(reminder)
        self._repository.add(reminder)
