"""Repositories built on top of the SQLite helper."""
from __future__ import annotations

from typing import Iterable, List, Optional

from . import db
from .models import Exercise, Note


class NoteRepository:
    def __init__(self, database: db.Database):
        self._database = database

    def create(self, content: str, source_type: str, metadata: Optional[dict] = None) -> Note:
        metadata = metadata or {}
        note = Note(content=content, source_type=source_type, metadata=metadata)
        with self._database.session() as connection:
            note = db.insert_note(connection, note)
        return note

    def list_all(self) -> List[Note]:
        with self._database.session() as connection:
            return db.list_notes(connection)


class ExerciseRepository:
    def __init__(self, database: db.Database):
        self._database = database

    def create(
        self,
        note_id: int,
        exercise_type: str,
        difficulty: str,
        payload: str,
        metadata: Optional[dict] = None,
    ) -> Exercise:
        metadata = metadata or {}
        exercise = Exercise(
            note_id=note_id,
            type=exercise_type,
            difficulty=difficulty,
            payload=payload,
            metadata=metadata,
        )
        with self._database.session() as connection:
            exercise = db.insert_exercise(connection, exercise)
        return exercise

    def list_for_note(self, note_id: int) -> List[Exercise]:
        with self._database.session() as connection:
            return db.list_exercises(connection, note_id)


__all__ = ["NoteRepository", "ExerciseRepository"]
