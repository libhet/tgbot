"""Application entry point providing FastAPI integration when available."""
from __future__ import annotations

import asyncio
from typing import Any, Dict

try:
    from fastapi import Depends, FastAPI, HTTPException, status
    from fastapi.middleware.cors import CORSMiddleware
except ImportError as exc:  # pragma: no cover - optional dependency for runtime
    raise RuntimeError(
        "FastAPI is required to run the HTTP API. Install optional dependencies to use this module."
    ) from exc

try:
    from prometheus_fastapi_instrumentator import Instrumentator
except ImportError:  # pragma: no cover - optional instrumentation
    Instrumentator = None  # type: ignore

try:
    import uvicorn
except ImportError:  # pragma: no cover - optional runtime
    uvicorn = None  # type: ignore

from .config import SETTINGS
from .database import get_session
from .localization.translator import translate
from .logging_config import configure_logging
from .services.auth import AuthenticationError, assert_user_allowed, get_or_create_user

configure_logging()
app = FastAPI(title="Telegram Learning Bot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialise application resources."""

    if Instrumentator:
        Instrumentator().instrument(app).expose(app)


@app.get("/health", tags=["system"])
async def healthcheck() -> Dict[str, str]:
    """Return a localized health status message."""

    return {"status": translate("health.ok")}


@app.post("/auth/telegram", tags=["auth"], status_code=status.HTTP_200_OK)
async def authenticate_telegram_user(
    payload: Dict[str, Any],
    db=Depends(get_session),
) -> Dict[str, Any]:
    """Register a Telegram user or return existing user data."""

    telegram_user_id = payload.get("telegram_user_id")
    if telegram_user_id is None:
        raise HTTPException(status_code=400, detail="telegram_user_id is required")

    locale = str(payload.get("locale") or SETTINGS.default_locale)
    try:
        user = await get_or_create_user(
            db,
            telegram_user_id=int(telegram_user_id),
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name"),
            username=payload.get("username"),
            locale=locale,
        )
        assert_user_allowed(user, SETTINGS.allowed_telegram_user_ids)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return {
        "user_id": user.id,
        "telegram_user_id": user.telegram_user_id,
        "locale": user.locale,
        "message": translate("auth.success", locale=user.locale),
    }


@app.get("/locales", tags=["system"])
async def list_locales() -> Dict[str, Any]:
    """Return supported locales."""

    return {"locales": SETTINGS.supported_locales}


async def run() -> None:
    """Run the application using Uvicorn if installed."""

    if uvicorn is None:
        raise RuntimeError("uvicorn is not installed. Install optional dependencies to run the server.")

    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":  # pragma: no cover - manual entry point
    asyncio.run(run())
