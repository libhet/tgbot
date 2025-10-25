"""Persistence layer for exercises."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .models import Exercise, HistoryEntry


class ExerciseRepository:
    """Repository that stores exercise data in a JSON document."""

    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path or Path.home() / ".exercise_tracker" / "exercises.json")
        if not self.path.parent.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write_payload({})

    def _read_payload(self) -> Dict[str, dict]:
        if not self.path.exists():
            return {}
        with self.path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return dict(data)

    def _write_payload(self, payload: Dict[str, dict]) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)

    def list(self) -> List[Exercise]:
        payload = self._read_payload()
        return [Exercise.deserialize(item) for item in payload.values()]

    def get(self, name: str) -> Optional[Exercise]:
        payload = self._read_payload()
        raw = payload.get(name)
        if not raw:
            return None
        return Exercise.deserialize(raw)

    def add_or_update(self, exercise: Exercise) -> None:
        payload = self._read_payload()
        payload[exercise.name] = exercise.serialize()
        self._write_payload(payload)

    def remove(self, name: str) -> bool:
        payload = self._read_payload()
        if name in payload:
            del payload[name]
            self._write_payload(payload)
            return True
        return False

    def sync(self, exercises: Iterable[Exercise]) -> None:
        payload = {exercise.name: exercise.serialize() for exercise in exercises}
        self._write_payload(payload)

    def append_history(self, name: str, entry: HistoryEntry) -> None:
        exercise = self.get(name)
        if not exercise:
            raise KeyError(f"Exercise '{name}' does not exist")
        entries = list(exercise.history)
        entries.append(entry)
        exercise.sync_history(entries)
        self.add_or_update(exercise)

    def ensure(self, name: str, target_repetitions: int) -> Exercise:
        exercise = self.get(name)
        if exercise is None:
            exercise = Exercise(name=name, target_repetitions=target_repetitions)
            self.add_or_update(exercise)
        return exercise
