from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Iterable, Mapping, Sequence

from app.schemas import CalendarDay, ExerciseRead, PracticeSessionRead


def render_exercise_list(exercises: Sequence[ExerciseRead]) -> str:
    if not exercises:
        return "❓ Пока нет доступных упражнений. Добавьте их через веб-интерфейс."
    lines: list[str] = ["📋 Список упражнений:"]
    for exercise in exercises:
        sessions_count = len(exercise.sessions)
        lines.append(
            f"\n• <b>{exercise.title}</b> ({exercise.type}, статус: {exercise.status})"
        )
        if exercise.description:
            lines.append(exercise.description)
        if sessions_count:
            lines.append(f"Запланировано сессий: {sessions_count}")
    return "\n".join(lines)


def render_calendar_view(
    days: Iterable[CalendarDay], *, exercise_lookup: Mapping[int, str] | None = None
) -> str:
    days = list(days)
    if not days:
        return "📅 Расписание пустое. Запланируйте первую сессию!"

    grouped: dict[date, list[PracticeSessionRead]] = defaultdict(list)
    for day in days:
        grouped[day.date].extend(day.sessions)

    lookup = dict(exercise_lookup or {})
    lines = ["📅 Ближайшие практики:"]
    for day, sessions in sorted(grouped.items()):
        lines.append(f"\n<b>{day.strftime('%d.%m.%Y')}</b>")
        for session in sessions:
            title = session.exercise_title or lookup.get(session.exercise_id)
            if not title:
                title = f"упражнение #{session.exercise_id}"
            lines.append(f"- {title} (статус: {session.status})")
    return "\n".join(lines)
