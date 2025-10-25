from __future__ import annotations

from collections import defaultdict
from datetime import date

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app import schemas, serializers
from app.crud import list_calendar_days, list_exercises
from app.database import SessionLocal

from .views import render_calendar_view, render_exercise_list

router = Router()

VIEW_LIST = "list"
VIEW_CALENDAR = "calendar"


class ViewCallback:
    prefix = "view:"

    @classmethod
    def data(cls, view: str) -> str:
        return f"{cls.prefix}{view}"

    @classmethod
    def parse(cls, data: str) -> str | None:
        if not data.startswith(cls.prefix):
            return None
        return data[len(cls.prefix) :]


def build_view_switcher(active: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📋 Список" + (" ✅" if active == VIEW_LIST else ""),
            callback_data=ViewCallback.data(VIEW_LIST),
        ),
        InlineKeyboardButton(
            text="📅 Календарь" + (" ✅" if active == VIEW_CALENDAR else ""),
            callback_data=ViewCallback.data(VIEW_CALENDAR),
        ),
    )
    return builder.as_markup()


def fetch_data() -> tuple[list[schemas.ExerciseRead], list[schemas.CalendarDay]]:
    with SessionLocal() as session:
        exercises = [
            serializers.exercise_to_schema(item)
            for item in list_exercises(session)
        ]
        raw_sessions = list_calendar_days(session)
        buckets: dict[date, list[schemas.PracticeSessionRead]] = defaultdict(list)
        for practice_session in raw_sessions:
            buckets[practice_session.date].append(
                serializers.session_to_schema(practice_session)
            )
        calendar = [
            schemas.CalendarDay(date=day, sessions=sessions)
            for day, sessions in sorted(buckets.items())
        ]
    return exercises, calendar


async def send_list_view(target: Message | CallbackQuery) -> None:
    exercises, _ = fetch_data()
    text = render_exercise_list(exercises)
    reply_markup = build_view_switcher(VIEW_LIST)
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
        await target.answer()
    else:
        await target.answer(text, reply_markup=reply_markup, parse_mode="HTML")


async def send_calendar_view(target: Message | CallbackQuery) -> None:
    exercises, calendar = fetch_data()
    lookup = {exercise.id: exercise.title for exercise in exercises}
    text = render_calendar_view(calendar, exercise_lookup=lookup)
    reply_markup = build_view_switcher(VIEW_CALENDAR)
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
        await target.answer()
    else:
        await target.answer(text, reply_markup=reply_markup, parse_mode="HTML")


@router.message(Command("start"))
async def handle_start(message: Message) -> None:
    await send_list_view(message)


@router.callback_query()
async def handle_view_switch(callback: CallbackQuery) -> None:
    view = ViewCallback.parse(callback.data or "")
    if view == VIEW_LIST:
        await send_list_view(callback)
    elif view == VIEW_CALENDAR:
        await send_calendar_view(callback)
    else:
        await callback.answer("Неизвестная команда", show_alert=True)
