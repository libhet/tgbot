"""Progress visualisation and reporting."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, timedelta
from typing import Dict, Iterable, List, Sequence, Tuple

from .models import Exercise, HistoryEntry

ANSI_RESET = "\033[0m"


def colorize(text: str, color_code: str) -> str:
    return f"\033[{color_code}m{text}{ANSI_RESET}"


def generate_repeat_buttons(exercise: Exercise) -> List[str]:
    """Return labels for repeat buttons (Повтор #1, ...)."""

    labels: List[str] = []
    for index in range(1, exercise.target_repetitions + 1):
        marker = "☑" if index <= exercise.completed_repetitions else "☐"
        labels.append(f"{marker} Повтор #{index}")
    return labels


def render_progress_board(exercises: Sequence[Exercise]) -> str:
    """Render a textual board with progress badges and percentages."""

    lines = ["Прогресс упражнений:"]
    for exercise in exercises:
        badge = exercise.status.badge
        color = exercise.status.color
        percentage = f"{exercise.completion_percentage():.0f}%"
        line = (
            f"- {colorize(badge, color)} {exercise.name}: "
            f"{exercise.completed_repetitions}/{exercise.target_repetitions} ({percentage})"
        )
        lines.append(line)
    return "\n".join(lines)


def _daterange(start: date, end: date) -> Iterable[date]:
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def render_progress_calendar(exercises: Sequence[Exercise], days: int = 7) -> str:
    """Render a calendar view for the given range of days."""

    if not exercises:
        return "Нет упражнений для отображения"

    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    entries_by_day: Dict[date, List[Tuple[str, HistoryEntry]]] = defaultdict(list)

    for exercise in exercises:
        for entry in exercise.iter_history():
            entry_date = entry.performed_at.date()
            if start_date <= entry_date <= end_date:
                entries_by_day[entry_date].append((exercise.name, entry))

    lines = ["Календарь прогресса:"]
    for current_date in _daterange(start_date, end_date):
        day_entries = entries_by_day.get(current_date, [])
        if not day_entries:
            lines.append(f"{current_date.isoformat()}: —")
            continue
        badges = ", ".join(
            f"{name} #{entry.repeat_index}" for name, entry in sorted(day_entries)
        )
        lines.append(f"{current_date.isoformat()}: {badges}")
    return "\n".join(lines)


def _start_of_week(some_date: date) -> date:
    return some_date - timedelta(days=some_date.weekday())


def _start_of_month(some_date: date) -> date:
    return some_date.replace(day=1)


def generate_statistics(exercises: Sequence[Exercise]) -> Dict[str, Dict[str, int]]:
    """Aggregate statistics for weekly and monthly reporting."""

    weekly: Counter[str] = Counter()
    monthly: Counter[str] = Counter()

    today = date.today()
    week_start = _start_of_week(today)
    month_start = _start_of_month(today)

    for exercise in exercises:
        for entry in exercise.iter_history():
            entry_date = entry.performed_at.date()
            if entry_date >= week_start:
                weekly[exercise.name] += 1
            if entry_date >= month_start:
                monthly[exercise.name] += 1

    return {
        "weekly": dict(weekly),
        "monthly": dict(monthly),
    }
