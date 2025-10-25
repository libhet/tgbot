from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration."""

    default_intervals: List[int] = Field(
        default_factory=lambda: [1, 3, 7, 14, 30],
        description="Default spaced repetition intervals in days.",
    )
    timezone: str = Field(
        default="UTC",
        description="Timezone used when calculating review dates.",
    )
    database_url: str = Field(
        default="sqlite:///./app.db",
        description="SQLAlchemy compatible database URL.",
    )

    model_config = {
        "env_prefix": "APP_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
