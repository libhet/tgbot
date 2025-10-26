from __future__ import annotations

from pathlib import Path

from tgnotes.services.pdf_importer import PdfImporter


class StubPage:
    def __init__(self, text: str):
        self._text = text

    def extract_text(self) -> str:
        return self._text


class StubDocument:
    def __init__(self, text: str):
        self.pages = [StubPage(text)]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class StubPdfBackend:
    def open(self, path: Path):
        return StubDocument(path.read_text())


def test_pdf_importer_reads_text(tmp_path: Path):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_text("Hello from PDF!")
    importer = PdfImporter(backend=StubPdfBackend())
    content = importer.parse(pdf_path)
    assert "Hello from PDF" in content
