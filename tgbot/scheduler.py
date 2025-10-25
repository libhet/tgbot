"""Polling scheduler built around a lightweight worker thread."""
from __future__ import annotations

import threading
from datetime import datetime, timedelta
from typing import Callable, Optional

from .notifications import NotificationService


class ReminderScheduler:
    """Runs :class:`NotificationService` periodically."""

    def __init__(
        self,
        service: NotificationService,
        poll_interval: timedelta = timedelta(minutes=1),
        now_func: Callable[[], datetime] = datetime.utcnow,
    ) -> None:
        self._service = service
        self._poll_interval = poll_interval
        self._now_func = now_func
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self) -> None:
        while not self._stop.is_set():
            self.run_pending()
            self._stop.wait(self._poll_interval.total_seconds())

    def stop(self) -> None:
        if not self._thread:
            return
        self._stop.set()
        self._thread.join()
        self._thread = None

    def run_pending(self) -> None:
        """Execute a single polling cycle."""

        now = self._now_func()
        self._service.send_due_reminders(now)
