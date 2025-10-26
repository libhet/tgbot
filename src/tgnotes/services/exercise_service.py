"""Service orchestrating exercise generation and persistence."""
from __future__ import annotations

from typing import Iterable, Optional

from ..models import Note
from ..repositories import ExerciseRepository
from .exercise_generator import ExerciseGenerator


class ExerciseService:
    """High-level service to create and store exercises."""

    def __init__(self, repository: ExerciseRepository, generator: Optional[ExerciseGenerator] = None):
        self._repository = repository
        self._generator = generator or ExerciseGenerator()

    def create_move_words(
        self,
        note: Note,
        lexical_units: Iterable[str],
        difficulty: str,
        metadata: Optional[dict] = None,
    ):
        payload = self._generator.generate_move_words(list(lexical_units))
        model = self._generator.as_model(note, payload, difficulty, metadata)
        return self._repository.create(
            note_id=model.note_id,
            exercise_type=model.type,
            difficulty=model.difficulty,
            payload=model.payload,
            metadata=model.metadata,
        )

    def create_recall_words(
        self,
        note: Note,
        lexical_units: Iterable[str],
        difficulty: str,
        metadata: Optional[dict] = None,
    ):
        payload = self._generator.generate_recall_words(list(lexical_units))
        model = self._generator.as_model(note, payload, difficulty, metadata)
        return self._repository.create(
            note_id=model.note_id,
            exercise_type=model.type,
            difficulty=model.difficulty,
            payload=model.payload,
            metadata=model.metadata,
        )


__all__ = ["ExerciseService"]
