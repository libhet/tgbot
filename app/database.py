"""Lightweight asynchronous database helper built on sqlite3."""
from __future__ import annotations

import asyncio
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, Optional

from .config import SETTINGS, project_root
from .models import Account, User

_DB_LOCK = asyncio.Lock()


def _resolve_database_path(database_url: str) -> Path:
    if database_url.startswith("sqlite:///"):
        relative_path = database_url.replace("sqlite:///", "", 1)
        return project_root() / relative_path
    raise RuntimeError("Only sqlite:/// URLs are supported in the lightweight runtime")


class Database:
    """Simple async-aware wrapper around sqlite3 for user data storage."""

    def __init__(self, database_url: str) -> None:
        self.path = _resolve_database_path(database_url)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        conn = self._connection()
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_user_id INTEGER UNIQUE NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    username TEXT,
                    locale TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    provider TEXT NOT NULL,
                    external_id TEXT NOT NULL,
                    access_token TEXT,
                    refresh_token TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, provider),
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
        conn.close()

    async def get_user_by_telegram_id(self, telegram_user_id: int) -> Optional[User]:
        async with _DB_LOCK:
            return await asyncio.to_thread(self._get_user_by_telegram_id_sync, telegram_user_id)

    def _get_user_by_telegram_id_sync(self, telegram_user_id: int) -> Optional[User]:
        conn = self._connection()
        cursor = conn.execute(
            "SELECT * FROM users WHERE telegram_user_id = ?", (telegram_user_id,)
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return User(
            id=row["id"],
            telegram_user_id=row["telegram_user_id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            username=row["username"],
            locale=row["locale"],
            is_active=bool(row["is_active"]),
        )

    async def save_user(self, user: User) -> User:
        async with _DB_LOCK:
            return await asyncio.to_thread(self._save_user_sync, user)

    def _save_user_sync(self, user: User) -> User:
        conn = self._connection()
        with conn:
            if user.id is None:
                cursor = conn.execute(
                    """
                    INSERT INTO users (
                        telegram_user_id, first_name, last_name, username, locale, is_active
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user.telegram_user_id,
                        user.first_name,
                        user.last_name,
                        user.username,
                        user.locale,
                        1 if user.is_active else 0,
                    ),
                )
                user.id = cursor.lastrowid
            else:
                conn.execute(
                    """
                    UPDATE users
                    SET first_name = ?, last_name = ?, username = ?, locale = ?, is_active = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        user.first_name,
                        user.last_name,
                        user.username,
                        user.locale,
                        1 if user.is_active else 0,
                        user.id,
                    ),
                )
        conn.close()
        return user

    async def link_account(self, account: Account) -> Account:
        async with _DB_LOCK:
            return await asyncio.to_thread(self._link_account_sync, account)

    def _link_account_sync(self, account: Account) -> Account:
        conn = self._connection()
        with conn:
            cursor = conn.execute(
                "SELECT id FROM accounts WHERE user_id = ? AND provider = ?",
                (account.user_id, account.provider),
            )
            row = cursor.fetchone()
            if row:
                conn.execute(
                    """
                    UPDATE accounts
                    SET external_id = ?, access_token = ?, refresh_token = ?, created_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        account.external_id,
                        account.access_token,
                        account.refresh_token,
                        row["id"],
                    ),
                )
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO accounts (user_id, provider, external_id, access_token, refresh_token)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        account.user_id,
                        account.provider,
                        account.external_id,
                        account.access_token,
                        account.refresh_token,
                    ),
                )
                account.id = cursor.lastrowid
        conn.close()
        return account


database = Database(SETTINGS.database_url)


@asynccontextmanager
def get_session() -> AsyncIterator[Database]:
    yield database
