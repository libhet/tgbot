from __future__ import annotations

import asyncio
import os

from aiogram import Bot, Dispatcher

from .handlers import register_handlers


async def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable is required")

    bot = Bot(token=token)
    dispatcher = Dispatcher()
    register_handlers(dispatcher)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":  # pragma: no cover - manual start helper
    asyncio.run(main())
