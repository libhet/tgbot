import asyncio
import os

import pytest

from app.config import get_settings
from app.database import Database
from app.services.auth import AuthenticationError, assert_user_allowed, get_or_create_user


@pytest.fixture(scope="module")
def db(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("data")
    db_path = temp_dir / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["TELEGRAM_BOT_TOKEN"] = "test-token"
    get_settings.cache_clear()  # type: ignore[attr-defined]
    get_settings()
    return Database(os.environ["DATABASE_URL"])


def run(coro):
    return asyncio.run(coro)


def test_get_or_create_user_creates_user(db: Database):
    user = run(get_or_create_user(db, telegram_user_id=123, locale="en"))
    assert user.telegram_user_id == 123
    assert user.id is not None


def test_get_or_create_user_updates_existing(db: Database):
    user = run(get_or_create_user(db, telegram_user_id=999, locale="en"))
    updated = run(
        get_or_create_user(db, telegram_user_id=999, locale="ru", first_name="Ivan")
    )
    assert updated.id == user.id
    assert updated.locale == "ru"
    assert updated.first_name == "Ivan"


def test_assert_user_allowed_passes(db: Database):
    user = run(get_or_create_user(db, telegram_user_id=777, locale="en"))
    assert_user_allowed(user, allowed_ids=[777, 888])


def test_assert_user_allowed_rejects(db: Database):
    user = run(get_or_create_user(db, telegram_user_id=555, locale="en"))
    with pytest.raises(AuthenticationError):
        assert_user_allowed(user, allowed_ids=[111, 222])
