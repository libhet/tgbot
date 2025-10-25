"""Exercise storage abstractions with serialization support."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Protocol

from .models import Exercise, ExercisePrompt, ExerciseType


class ExerciseStorage(Protocol):
    """Protocol for storing and retrieving exercises."""

    def save(self, exercise: Exercise) -> None:
        ...

    def load_all(self) -> Iterable[Exercise]:
        ...


@dataclass
class JsonExerciseRecord:
    type: str
    prompt: Dict[str, object]
    solution: List[str]
    metadata: Dict[str, object]

    @classmethod
    def from_exercise(cls, exercise: Exercise) -> "JsonExerciseRecord":
        return cls(
            type=exercise.type.value,
            prompt=asdict(exercise.prompt),
            solution=list(exercise.solution),
            metadata=dict(exercise.metadata),
        )

    def to_exercise(self) -> Exercise:
        prompt = ExercisePrompt(
            instruction=str(self.prompt["instruction"]),
            context=self.prompt.get("context"),
            options=self.prompt.get("options"),
            hints=list(self.prompt.get("hints", [])),
        )
        return Exercise(
            type=ExerciseType.from_storage_key(self.type),
            prompt=prompt,
            solution=list(self.solution),
            metadata=dict(self.metadata),
        )


class InMemoryExerciseStorage:
    """Simple in-memory storage useful for tests and prototyping."""

    def __init__(self) -> None:
        self._items: List[Exercise] = []

    def save(self, exercise: Exercise) -> None:
        self._items.append(exercise)

    def load_all(self) -> Iterable[Exercise]:
        return list(self._items)


class JsonFileExerciseStorage:
    """Persists exercises in a JSON file."""

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path

    def save(self, exercise: Exercise) -> None:
        records = [JsonExerciseRecord.from_exercise(item) for item in self.load_all()]
        records.append(JsonExerciseRecord.from_exercise(exercise))
        data = [record.__dict__ for record in records]
        self._file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_all(self) -> Iterable[Exercise]:
        if not self._file_path.exists():
            return []
        raw = json.loads(self._file_path.read_text(encoding="utf-8"))
        return [JsonExerciseRecord(**item).to_exercise() for item in raw]

