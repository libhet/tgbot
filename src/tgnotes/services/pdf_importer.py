"""PDF importing service."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    import pdfplumber  # type: ignore
except Exception:  # pragma: no cover - graceful fallback when dependency missing
    pdfplumber = None  # type: ignore


class PdfImporter:
    """Extract text from PDF documents."""

    def __init__(self, backend: Optional[object] = None):
        self._backend = backend or pdfplumber

    def parse(self, pdf_path: str | Path) -> str:
        if self._backend is None:
            raise RuntimeError("pdfplumber is required to parse PDF files.")

        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(path)

        texts: list[str] = []
        with self._backend.open(path) as pdf:  # type: ignore[attr-defined]
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                texts.append(page_text.strip())
        return "\n".join(filter(None, texts)).strip()


__all__ = ["PdfImporter"]
