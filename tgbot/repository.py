"""Reminder storage interfaces."""
from __future__ import annotations

from datetime import datetime
from threading import RLock
from typing import Dict, Iterable, List

from .models import Reminder


class ReminderRepository:
    """Abstract base for reminder persistence."""

    def add(self, reminder: Reminder) -> None:
        raise NotImplementedError

    def remove(self, reminder_id: str) -> None:
        raise NotImplementedError

    def get(self, reminder_id: str) -> Reminder:
        raise NotImplementedError

    def list_due(self, moment: datetime) -> Iterable[Reminder]:
        raise NotImplementedError

    def update(self, reminder: Reminder) -> None:
        raise NotImplementedError


class InMemoryReminderRepository(ReminderRepository):
    """Thread-safe in-memory repository used in tests and local runs."""

    def __init__(self) -> None:
        self._reminders: Dict[str, Reminder] = {}
        self._lock = RLock()

    def add(self, reminder: Reminder) -> None:
        with self._lock:
            self._reminders[reminder.reminder_id] = reminder

    def remove(self, reminder_id: str) -> None:
        with self._lock:
            self._reminders.pop(reminder_id, None)

    def get(self, reminder_id: str) -> Reminder:
        with self._lock:
            return self._reminders[reminder_id]

    def list_due(self, moment: datetime) -> Iterable[Reminder]:
        with self._lock:
            return [rem for rem in self._reminders.values() if rem.scheduled_at <= moment]

    def update(self, reminder: Reminder) -> None:
        with self._lock:
            if reminder.reminder_id not in self._reminders:
                raise KeyError(f"Reminder {reminder.reminder_id} is not stored")
            self._reminders[reminder.reminder_id] = reminder

    # Helper for tests
    def all(self) -> List[Reminder]:
        with self._lock:
            return list(self._reminders.values())
