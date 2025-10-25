from __future__ import annotations

from tgnotes.services.web_importer import WebContentImporter


def stub_fetcher(url: str, notion_api_token: str | None = None) -> str:
    return "<html><body><h1>Title</h1><p>Paragraph content.</p></body></html>"


def test_web_importer_extracts_text():
    importer = WebContentImporter(fetcher=stub_fetcher)
    result = importer.fetch("https://example.com/page")

    assert result.url == "https://example.com/page"
    assert "Title" in result.text
    assert "Paragraph content." in result.text
