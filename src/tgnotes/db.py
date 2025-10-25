"""Lightweight SQLite helpers for persisting notes and exercises."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from .models import Exercise, Note

DEFAULT_DB_PATH = Path("app.db")


class Database:
    """Simple wrapper around SQLite connections."""

    def __init__(self, path: str | Path = DEFAULT_DB_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    @contextmanager
    def session(self) -> Generator[sqlite3.Connection, None, None]:
        connection = self.connect()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()


def init_db(database: Database) -> None:
    with database.session() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                source_type TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                payload TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(note_id) REFERENCES notes(id) ON DELETE CASCADE
            )
            """
        )


def _row_to_note(row: sqlite3.Row) -> Note:
    return Note(
        id=row["id"],
        content=row["content"],
        source_type=row["source_type"],
        metadata=json.loads(row["metadata"]),
        created_at=_parse_datetime(row["created_at"]),
    )


def _row_to_exercise(row: sqlite3.Row) -> Exercise:
    return Exercise(
        id=row["id"],
        note_id=row["note_id"],
        type=row["type"],
        difficulty=row["difficulty"],
        payload=row["payload"],
        metadata=json.loads(row["metadata"]),
        created_at=_parse_datetime(row["created_at"]),
    )


def _parse_datetime(value: str):
    from datetime import datetime

    return datetime.fromisoformat(value)


def insert_note(connection: sqlite3.Connection, note: Note) -> Note:
    cursor = connection.execute(
        "INSERT INTO notes (content, source_type, metadata, created_at) VALUES (?, ?, ?, ?)",
        (note.content, note.source_type, json.dumps(note.metadata), note.created_at.isoformat()),
    )
    note.id = cursor.lastrowid
    return note


def insert_exercise(connection: sqlite3.Connection, exercise: Exercise) -> Exercise:
    cursor = connection.execute(
        """
        INSERT INTO exercises (note_id, type, difficulty, payload, metadata, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            exercise.note_id,
            exercise.type,
            exercise.difficulty,
            exercise.payload,
            json.dumps(exercise.metadata),
            exercise.created_at.isoformat(),
        ),
    )
    exercise.id = cursor.lastrowid
    return exercise


def list_exercises(connection: sqlite3.Connection, note_id: int) -> list[Exercise]:
    cursor = connection.execute("SELECT * FROM exercises WHERE note_id = ? ORDER BY id", (note_id,))
    return [_row_to_exercise(row) for row in cursor.fetchall()]


def list_notes(connection: sqlite3.Connection) -> list[Note]:
    cursor = connection.execute("SELECT * FROM notes ORDER BY id")
    return [_row_to_note(row) for row in cursor.fetchall()]


__all__ = [
    "Database",
    "DEFAULT_DB_PATH",
    "init_db",
    "insert_note",
    "insert_exercise",
    "list_notes",
    "list_exercises",
]
