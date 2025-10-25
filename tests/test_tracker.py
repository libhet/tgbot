from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from exercise_tracker.cli import CLI
from exercise_tracker.models import Exercise, ExerciseStatus
from exercise_tracker.progress import (
    generate_repeat_buttons,
    generate_statistics,
    render_progress_board,
    render_progress_calendar,
)
from exercise_tracker.storage import ExerciseRepository


@pytest.fixture()
def repo(tmp_path: Path) -> ExerciseRepository:
    return ExerciseRepository(path=tmp_path / "data.json")


def test_exercise_status_transitions() -> None:
    exercise = Exercise(name="Отжимания", target_repetitions=3)
    assert exercise.status is ExerciseStatus.PENDING
    exercise.add_history_entry(datetime.utcnow())
    assert exercise.status is ExerciseStatus.IN_PROGRESS
    exercise.add_history_entry(datetime.utcnow())
    exercise.add_history_entry(datetime.utcnow())
    assert exercise.status is ExerciseStatus.COMPLETED
    with pytest.raises(ValueError):
        exercise.add_history_entry()


def test_repeat_buttons_show_progress() -> None:
    exercise = Exercise(name="Приседания", target_repetitions=3)
    exercise.add_history_entry(datetime.utcnow())
    buttons = generate_repeat_buttons(exercise)
    assert buttons == ["☑ Повтор #1", "☐ Повтор #2", "☐ Повтор #3"]


def test_progress_board_renders_badges(repo: ExerciseRepository) -> None:
    repo.ensure("Берпи", 2)
    repo.ensure("Планка", 1)
    cli = CLI(repo)
    output = cli.list()
    assert "Прогресс упражнений:" in output


def test_calendar_displays_recent_activity() -> None:
    exercise = Exercise(name="Скручивания", target_repetitions=2)
    exercise.add_history_entry(datetime.utcnow())
    exercise.add_history_entry(datetime.utcnow() - timedelta(days=1))
    calendar = render_progress_calendar([exercise], days=2)
    assert "Календарь прогресса:" in calendar
    assert exercise.name in calendar


def test_statistics_group_by_periods() -> None:
    exercise = Exercise(name="Бег", target_repetitions=5)
    now = datetime.utcnow()
    exercise.add_history_entry(now)
    exercise.add_history_entry(now - timedelta(days=3))
    another = Exercise(name="Пресс", target_repetitions=2)
    another.add_history_entry(now - timedelta(days=20))
    stats = generate_statistics([exercise, another])
    assert stats["weekly"]["Бег"] >= 1
    assert "Пресс" in stats["monthly"]
