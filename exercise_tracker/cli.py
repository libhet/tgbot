"""Command line interface for the exercise tracker."""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .models import Exercise
from .progress import (
    generate_repeat_buttons,
    generate_statistics,
    render_progress_board,
    render_progress_calendar,
)
from .storage import ExerciseRepository


class CLI:
    def __init__(self, repository: ExerciseRepository) -> None:
        self.repository = repository

    def add(self, name: str, target_repetitions: int) -> None:
        exercise = self.repository.ensure(name, target_repetitions)
        exercise.target_repetitions = target_repetitions
        self.repository.add_or_update(exercise)

    def list(self) -> str:
        exercises = sorted(self.repository.list(), key=lambda exercise: exercise.name)
        return render_progress_board(exercises)

    def calendar(self, days: int) -> str:
        exercises = sorted(self.repository.list(), key=lambda exercise: exercise.name)
        return render_progress_calendar(exercises, days=days)

    def mark(self, name: str) -> str:
        exercise = self.repository.get(name)
        if exercise is None:
            raise SystemExit(f"Упражнение '{name}' не найдено")
        entry = exercise.add_history_entry(datetime.utcnow())
        self.repository.add_or_update(exercise)
        buttons = ", ".join(generate_repeat_buttons(exercise))
        status = "выполнено" if exercise.is_completed() else "в процессе"
        return (
            f"Добавлен {entry.repeat_index}-й повтор для '{exercise.name}'. "
            f"Статус: {status}.\nКнопки: {buttons}"
        )

    def report(self) -> str:
        exercises = self.repository.list()
        stats = generate_statistics(exercises)
        lines = ["Статистика:"]
        lines.append("Неделя:")
        if stats["weekly"]:
            for name, count in stats["weekly"].items():
                lines.append(f"  - {name}: {count}")
        else:
            lines.append("  —")
        lines.append("Месяц:")
        if stats["monthly"]:
            for name, count in stats["monthly"].items():
                lines.append(f"  - {name}: {count}")
        else:
            lines.append("  —")
        return "\n".join(lines)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Exercise tracker CLI")
    parser.add_argument(
        "--storage",
        type=Path,
        default=None,
        help="Путь к файлу хранения (по умолчанию ~/.exercise_tracker/exercises.json)",
    )
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add", help="Добавить упражнение")
    add_parser.add_argument("name")
    add_parser.add_argument("target", type=int)

    subparsers.add_parser("list", help="Показать прогресс")

    calendar_parser = subparsers.add_parser("calendar", help="Календарь прогресса")
    calendar_parser.add_argument("--days", type=int, default=7)

    mark_parser = subparsers.add_parser("mark", help="Отметить повтор")
    mark_parser.add_argument("name")

    subparsers.add_parser("report", help="Статистика по неделе и месяцу")

    return parser


def main(argv: Iterable[str] | None = None) -> str:
    parser = create_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    repo = ExerciseRepository(path=args.storage)
    cli = CLI(repo)

    command = args.command
    if command == "add":
        cli.add(args.name, args.target)
        return f"Упражнение '{args.name}' добавлено"
    if command == "list":
        return cli.list()
    if command == "calendar":
        return cli.calendar(args.days)
    if command == "mark":
        return cli.mark(args.name)
    if command == "report":
        return cli.report()
    parser.print_help()
    return ""


if __name__ == "__main__":
    print(main())
