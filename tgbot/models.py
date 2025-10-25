"""Data models for notification scheduling."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Optional


@dataclass
class NotificationSettings:
    """Preferences that influence when reminders are delivered."""

    user_id: int
    frequency: timedelta = field(default=timedelta(hours=24))
    quiet_hours_start: Optional[time] = None
    quiet_hours_end: Optional[time] = None

    def is_quiet_time(self, moment: datetime) -> bool:
        """Return ``True`` when the provided ``moment`` falls inside quiet hours."""

        if self.quiet_hours_start is None or self.quiet_hours_end is None:
            return False

        quiet_start = self.quiet_hours_start
        quiet_end = self.quiet_hours_end
        current_time = moment.time()

        if quiet_start == quiet_end:
            # Same value means quiet hours disabled (covers 0 minutes).
            return False

        if quiet_start < quiet_end:
            return quiet_start <= current_time < quiet_end

        # Quiet hours wrap around midnight (e.g. 22:00 - 07:00)
        return current_time >= quiet_start or current_time < quiet_end


@dataclass
class Reminder:
    """Represents a scheduled notification."""

    reminder_id: str
    user_id: int
    chat_id: int
    message: str
    scheduled_at: datetime
    reply_markup: Optional[dict] = None

    def snooze(self, delay: timedelta) -> None:
        """Postpone the reminder by ``delay`` duration."""

        self.scheduled_at = self.scheduled_at + delay

    def postpone(self, new_time: datetime) -> None:
        """Move the reminder to an absolute ``new_time``."""

        self.scheduled_at = new_time
