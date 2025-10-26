"""Utility helpers for backing up the database."""
from __future__ import annotations

import datetime as dt
import os
import subprocess
from pathlib import Path
from typing import Optional

from ..config import SETTINGS, project_root


BACKUP_DIR = project_root() / "backups"


def ensure_backup_dir() -> Path:
    """Ensure that the backup directory exists."""

    BACKUP_DIR.mkdir(exist_ok=True)
    return BACKUP_DIR


def pg_dump(database_url: str | None = None, *, destination: Optional[Path] = None) -> Path:
    """Create a PostgreSQL dump using pg_dump if available."""

    db_url = database_url or SETTINGS.database_url
    if not db_url.startswith("postgresql"):
        raise ValueError("pg_dump backups are only supported for PostgreSQL databases")

    ensure_backup_dir()
    timestamp = dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    destination = destination or (BACKUP_DIR / f"backup-{timestamp}.sql")

    env = os.environ.copy()
    env.setdefault("PGPASSWORD", env.get("DATABASE_PASSWORD", ""))

    subprocess.run(
        ["pg_dump", db_url, "-f", str(destination)],
        check=True,
        env=env,
    )
    return destination
