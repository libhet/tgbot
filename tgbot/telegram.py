"""Minimal Telegram Bot API client with pluggable HTTP backend."""
from __future__ import annotations

import json
from typing import Any, Dict, Optional
from urllib import request


class TelegramHTTPClient:
    """Simple HTTP client wrapper that posts JSON payloads."""

    def __init__(self) -> None:
        self._opener = request.build_opener()

    def post_json(self, url: str, payload: Dict[str, Any], timeout: Optional[float] = None) -> Dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with self._opener.open(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
        return json.loads(raw)


class TelegramAPIClient:
    """Client used by the notification service to talk to Telegram."""

    def __init__(self, token: str, http_client: Optional[TelegramHTTPClient] = None, timeout: Optional[float] = 10.0) -> None:
        self._token = token
        self._http_client = http_client or TelegramHTTPClient()
        self._timeout = timeout

    def _url(self, method: str) -> str:
        return f"https://api.telegram.org/bot{self._token}/{method}"

    def send_message(self, chat_id: int, text: str, reply_markup: Optional[Dict[str, Any]] = None, disable_notification: bool = False) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_notification": disable_notification,
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self._http_client.post_json(self._url("sendMessage"), payload, timeout=self._timeout)

    def answer_callback(self, callback_query_id: str, text: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        return self._http_client.post_json(self._url("answerCallbackQuery"), payload, timeout=self._timeout)

    def edit_message(self, chat_id: int, message_id: int, text: str) -> Dict[str, Any]:
        payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"}
        return self._http_client.post_json(self._url("editMessageText"), payload, timeout=self._timeout)
