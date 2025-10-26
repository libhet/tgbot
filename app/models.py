"""Domain models for the application."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    telegram_user_id: int
    id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    locale: str = "en"
    is_active: bool = True


@dataclass
class Account:
    user_id: int
    provider: str
    external_id: str
    id: Optional[int] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
