"""Exercise generation from processed text."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Sequence

from ..models import Exercise, Note


@dataclass(slots=True)
class ExercisePayload:
    type: str
    words: List[str]
    body: str

    def serialize(self) -> str:
        header = f"type: {self.type}\nwords: {', '.join(self.words)}\nexercise_start"
        return f"{header}\n{self.body.strip()}\nexercise_end"


class ExerciseGenerator:
    """Generate exercises based on lexical units."""

    def __init__(self, min_words: int = 3, max_words: int = 10):
        self._min_words = min_words
        self._max_words = max_words

    def _select_words(self, lexical_units: Sequence[str]) -> List[str]:
        words = [word for word in lexical_units if word.isalpha()]
        return words[: self._max_words]

    def generate_move_words(self, lexical_units: Sequence[str]) -> ExercisePayload:
        words = self._select_words(lexical_units)
        if len(words) < self._min_words:
            raise ValueError("Not enough lexical units to generate move_words exercise")
        body_lines = [f"- Move the word '{word}' into a meaningful sentence." for word in words]
        return ExercisePayload(type="move_words", words=words, body="\n".join(body_lines))

    def generate_recall_words(self, lexical_units: Sequence[str]) -> ExercisePayload:
        words = self._select_words(lexical_units)
        if len(words) < self._min_words:
            raise ValueError("Not enough lexical units to generate recall_words exercise")
        body_lines = [f"- Recall a definition or usage example for '{word}'." for word in words]
        return ExercisePayload(type="recall_words", words=words, body="\n".join(body_lines))

    def as_model(
        self,
        note: Note,
        payload: ExercisePayload,
        difficulty: str,
        metadata: dict | None = None,
    ) -> Exercise:
        if note.id is None:
            raise ValueError("Note must be persisted before generating exercises")
        metadata = metadata or {}
        combined_metadata = {
            **metadata,
            "words": payload.words,
            "generated_at": datetime.utcnow().isoformat(),
        }
        return Exercise(
            note_id=note.id,
            type=payload.type,
            difficulty=difficulty,
            payload=payload.serialize(),
            metadata=combined_metadata,
        )


__all__ = ["ExerciseGenerator", "ExercisePayload"]
