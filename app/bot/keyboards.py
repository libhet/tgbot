from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def manage_plan_keyboard(schedule_id: int) -> InlineKeyboardMarkup:
    """Return inline keyboard for managing a spaced repetition schedule."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Перенести",
                    callback_data=f"postpone:{schedule_id}",
                ),
                InlineKeyboardButton(
                    text="Добавить повтор",
                    callback_data=f"add_repeat:{schedule_id}",
                ),
            ]
        ]
    )
