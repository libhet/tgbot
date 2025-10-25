"""Import content from web pages or Notion documents."""
from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Callable, Optional
from urllib.request import Request, urlopen


@dataclass(slots=True)
class WebContent:
    url: str
    raw_html: str
    text: str


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:  # pragma: no cover - trivial
        stripped = data.strip()
        if stripped:
            self._parts.append(stripped)

    def extract(self, html: str) -> str:
        self._parts.clear()
        self.feed(html)
        return "\n".join(self._parts)


class WebContentImporter:
    """Fetch and extract textual content from a URL."""

    def __init__(self, fetcher: Optional[Callable[[str, Optional[str]], str]] = None):
        self._fetcher = fetcher or self._default_fetch
        self._parser = _TextExtractor()

    def _default_fetch(self, url: str, notion_api_token: Optional[str] = None) -> str:
        request = Request(url)
        if notion_api_token:
            request.add_header("Authorization", f"Bearer {notion_api_token}")
            request.add_header("Notion-Version", "2022-06-28")
        with urlopen(request) as response:  # type: ignore[call-arg]
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset)

    def fetch(self, url: str, notion_api_token: Optional[str] = None) -> WebContent:
        html = self._fetcher(url, notion_api_token)
        text = self._parser.extract(html)
        return WebContent(url=url, raw_html=html, text=text)


__all__ = ["WebContent", "WebContentImporter"]
