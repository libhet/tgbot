from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tgnotes.db import Database, init_db  # noqa: E402


@pytest.fixture()
def temp_database(tmp_path: Path) -> Database:
    db_path = tmp_path / "test.db"
    database = Database(db_path)
    init_db(database)
    return database


@pytest.fixture()
def sample_text() -> str:
    return "Learning languages is fun when exercises are engaging."
