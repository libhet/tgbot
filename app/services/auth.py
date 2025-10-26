"""Authentication and authorization services."""
from __future__ import annotations

from typing import Optional

from ..config import SETTINGS
from ..database import Database
from ..models import Account, User


class AuthenticationError(Exception):
    """Raised when authentication fails."""


async def get_or_create_user(
    db: Database,
    *,
    telegram_user_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    username: Optional[str] = None,
    locale: Optional[str] = None,
) -> User:
    """Fetch existing user or create a new one."""

    user = await db.get_user_by_telegram_id(telegram_user_id)
    if user:
        updated = False
        if locale and locale != user.locale:
            user.locale = locale
            updated = True
        if first_name and first_name != user.first_name:
            user.first_name = first_name
            updated = True
        if last_name and last_name != user.last_name:
            user.last_name = last_name
            updated = True
        if username and username != user.username:
            user.username = username
            updated = True
        if updated:
            await db.save_user(user)
        return user

    user = User(
        telegram_user_id=telegram_user_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
        locale=locale or SETTINGS.default_locale,
    )
    return await db.save_user(user)


async def link_account(
    db: Database,
    *,
    user: User,
    provider: str,
    external_id: str,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
) -> Account:
    """Link an external provider account to the user."""

    account = Account(
        user_id=user.id or 0,
        provider=provider,
        external_id=external_id,
        access_token=access_token,
        refresh_token=refresh_token,
    )
    return await db.link_account(account)


def assert_user_allowed(user: User, allowed_ids: list[int]) -> None:
    """Ensure that user is authorized to access restricted functionality."""

    if allowed_ids and user.telegram_user_id not in allowed_ids:
        raise AuthenticationError("User is not permitted to access this resource.")


__all__ = [
    "AuthenticationError",
    "assert_user_allowed",
    "get_or_create_user",
    "link_account",
]
