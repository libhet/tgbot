from __future__ import annotations

import os
from datetime import datetime, timedelta

import httpx
from aiogram import F, Dispatcher, Router
from aiogram.types import CallbackQuery

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

router = Router()


async def _call_api(method: str, path: str, payload: dict) -> dict:
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=10.0) as client:
        response = await client.request(method, path, json=payload)
        response.raise_for_status()
        return response.json()


@router.callback_query(F.data.startswith("postpone:"))
async def handle_postpone(callback: CallbackQuery) -> None:
    schedule_id = int(callback.data.split(":", 1)[1])
    new_date = datetime.utcnow() + timedelta(days=1)
    await _call_api(
        "POST",
        f"/schedules/{schedule_id}/reschedule",
        {"next_review_at": new_date.isoformat()},
    )
    if callback.message:
        await callback.message.answer("Повтор перенесён на завтра")
    await callback.answer()


@router.callback_query(F.data.startswith("add_repeat:"))
async def handle_add_repeat(callback: CallbackQuery) -> None:
    schedule_id = int(callback.data.split(":", 1)[1])
    await _call_api(
        "POST",
        f"/schedules/{schedule_id}/history",
        {"success": True, "reviewed_at": datetime.utcnow().isoformat()},
    )
    if callback.message:
        await callback.message.answer("Повтор зафиксирован как успешный")
    await callback.answer()


def register_handlers(dispatcher: Dispatcher) -> None:
    """Attach bot handlers to dispatcher."""

    dispatcher.include_router(router)
