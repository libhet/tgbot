"""Simple runtime localization utilities."""
from __future__ import annotations

from typing import Dict

from ..config import SETTINGS


class TranslationNotFoundError(KeyError):
    """Raised when a translation string is missing."""


TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "auth.success": "Authentication successful.",
        "auth.forbidden": "You are not allowed to use this bot.",
        "health.ok": "Service operational",
    },
    "ru": {
        "auth.success": "Аутентификация выполнена успешно.",
        "auth.forbidden": "У вас нет доступа к этому боту.",
        "health.ok": "Сервис работает",
    },
}


def translate(key: str, locale: str | None = None) -> str:
    """Return a localized string for the given key."""

    selected_locale = (locale or SETTINGS.default_locale).lower()
    if selected_locale not in SETTINGS.supported_locales:
        selected_locale = SETTINGS.default_locale

    locale_catalog = TRANSLATIONS.get(selected_locale)
    if not locale_catalog or key not in locale_catalog:
        raise TranslationNotFoundError(f"Translation '{key}' not found for locale '{selected_locale}'.")
    return locale_catalog[key]
