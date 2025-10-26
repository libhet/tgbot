"""Application configuration management using environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Callable, List, Optional, TypeVar

T = TypeVar("T")
DEFAULT_SUPPORTED_LOCALES = ["en", "ru"]


@dataclass
class Settings:
    telegram_bot_token: str
    telegram_api_url: str = "https://api.telegram.org"
    database_url: str = "sqlite:///app.db"
    ocr_api_key: Optional[str] = None
    ocr_endpoint: Optional[str] = None
    allowed_telegram_user_ids: List[int] = field(default_factory=list)
    default_locale: str = "en"
    supported_locales: List[str] = field(default_factory=lambda: DEFAULT_SUPPORTED_LOCALES.copy())
    sentry_dsn: Optional[str] = None

    @staticmethod
    def _split_list(raw_value: str, *, cast: Callable[[str], T] | None = None) -> List[T] | List[str]:
        values = [value.strip() for value in raw_value.split(",") if value.strip()]
        if cast is None:
            return values
        return [cast(value) for value in values]

    @classmethod
    def load(cls) -> "Settings":
        env = os.environ
        telegram_bot_token = env.get("TELEGRAM_BOT_TOKEN", "placeholder-token")

        allowed_ids_raw = env.get("ALLOWED_TELEGRAM_USER_IDS", "")
        supported_locales_raw = env.get("SUPPORTED_LOCALES", "")
        allowed_ids = cls._split_list(allowed_ids_raw, cast=int) if allowed_ids_raw else []
        supported_locales: List[str]
        if supported_locales_raw:
            supported_locales = [
                locale.lower() for locale in cls._split_list(supported_locales_raw)
            ]
        else:
            supported_locales = DEFAULT_SUPPORTED_LOCALES.copy()

        return cls(
            telegram_bot_token=telegram_bot_token,
            telegram_api_url=env.get("TELEGRAM_API_URL", cls.telegram_api_url),
            database_url=env.get("DATABASE_URL", cls.database_url),
            ocr_api_key=env.get("OCR_API_KEY"),
            ocr_endpoint=env.get("OCR_ENDPOINT"),
            allowed_telegram_user_ids=allowed_ids,  # type: ignore[arg-type]
            default_locale=env.get("DEFAULT_LOCALE", cls.default_locale),
            supported_locales=supported_locales,
            sentry_dsn=env.get("SENTRY_DSN"),
        )


def project_root() -> Path:
    """Return the absolute path to the project root directory."""

    return Path(__file__).resolve().parents[1]


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings.load()


SETTINGS = get_settings()
