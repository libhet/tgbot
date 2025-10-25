"""Domain entities for the exercise tracker."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Iterable, List, Sequence


class ExerciseStatus(str, Enum):
    """Enumeration of possible exercise states."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

    @property
    def badge(self) -> str:
        """Return a user friendly badge for the status."""

        return {
            ExerciseStatus.PENDING: "⌛",
            ExerciseStatus.IN_PROGRESS: "🔄",
            ExerciseStatus.COMPLETED: "✅",
        }[self]

    @property
    def color(self) -> str:
        """ANSI color code for the status."""

        return {
            ExerciseStatus.PENDING: "33",  # yellow
            ExerciseStatus.IN_PROGRESS: "36",  # cyan
            ExerciseStatus.COMPLETED: "32",  # green
        }[self]


@dataclass(frozen=True)
class HistoryEntry:
    """Single attempt of an exercise."""

    performed_at: datetime
    repeat_index: int

    def serialize(self) -> dict:
        return {
            "performed_at": self.performed_at.isoformat(),
            "repeat_index": self.repeat_index,
        }

    @staticmethod
    def deserialize(payload: dict) -> "HistoryEntry":
        return HistoryEntry(
            performed_at=datetime.fromisoformat(payload["performed_at"]),
            repeat_index=int(payload["repeat_index"]),
        )


@dataclass
class Exercise:
    """Exercise definition with progress tracking."""

    name: str
    target_repetitions: int
    history: List[HistoryEntry] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.target_repetitions < 1:
            raise ValueError("target_repetitions must be greater than zero")

    @property
    def completed_repetitions(self) -> int:
        """Number of repetitions already performed."""

        return len(self.history)

    @property
    def status(self) -> ExerciseStatus:
        """Return the current status of the exercise."""

        if self.completed_repetitions == 0:
            return ExerciseStatus.PENDING
        if self.completed_repetitions < self.target_repetitions:
            return ExerciseStatus.IN_PROGRESS
        return ExerciseStatus.COMPLETED

    def next_repeat_index(self) -> int:
        """Return the index of the next repetition."""

        return min(self.completed_repetitions + 1, self.target_repetitions)

    def add_history_entry(self, performed_at: datetime | None = None) -> HistoryEntry:
        """Register a new repetition for the exercise."""

        if self.status is ExerciseStatus.COMPLETED:
            raise ValueError(f"Exercise '{self.name}' already completed")

        entry = HistoryEntry(
            performed_at=performed_at or datetime.utcnow(),
            repeat_index=self.completed_repetitions + 1,
        )
        self.history.append(entry)
        return entry

    def is_completed(self) -> bool:
        return self.status is ExerciseStatus.COMPLETED

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "target_repetitions": self.target_repetitions,
            "history": [entry.serialize() for entry in self.history],
        }

    @staticmethod
    def deserialize(payload: dict) -> "Exercise":
        history = [HistoryEntry.deserialize(item) for item in payload.get("history", [])]
        return Exercise(
            name=payload["name"],
            target_repetitions=int(payload["target_repetitions"]),
            history=history,
        )

    def repeats_left(self) -> int:
        return max(self.target_repetitions - self.completed_repetitions, 0)

    def iter_history(self) -> Sequence[HistoryEntry]:
        return tuple(sorted(self.history, key=lambda entry: entry.performed_at))

    def __str__(self) -> str:
        return f"{self.name} ({self.completed_repetitions}/{self.target_repetitions})"

    def progress_ratio(self) -> float:
        if self.target_repetitions == 0:
            return 0.0
        return min(self.completed_repetitions / self.target_repetitions, 1.0)

    def completion_percentage(self) -> float:
        return self.progress_ratio() * 100

    def ensure_history_consistency(self) -> None:
        """Ensure sequential repeat indexes."""

        for index, entry in enumerate(self.iter_history(), start=1):
            if entry.repeat_index != index:
                raise ValueError(
                    "History entries are out of order for exercise '%s'" % self.name
                )

    def sync_history(self, entries: Iterable[HistoryEntry]) -> None:
        self.history = list(sorted(entries, key=lambda entry: entry.performed_at))
