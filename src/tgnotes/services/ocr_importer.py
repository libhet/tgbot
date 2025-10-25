"""OCR importing service."""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Protocol

try:  # pragma: no cover - optional dependency
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover
    Image = None  # type: ignore

try:  # pragma: no cover - optional dependency
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover
    pytesseract = None  # type: ignore


class OcrEngine(Protocol):
    def image_to_string(self, image) -> str:  # pragma: no cover - protocol definition
        ...


class OcrImporter:
    """Extract text from images using OCR."""

    def __init__(self, engine: Optional[OcrEngine] = None):
        self._engine = engine or pytesseract
        if self._engine is None:
            raise RuntimeError("An OCR engine such as pytesseract is required for OCR support.")

    def parse(self, image_path: str | Path) -> str:
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(path)

        if Image is None:
            with path.open("rb") as binary:
                data = binary.read()
            text = self._engine.image_to_string(data)  # type: ignore[arg-type]
        else:
            with Image.open(path) as image:  # type: ignore[call-arg]
                text = self._engine.image_to_string(image)  # type: ignore[call-arg]
        return text.strip()


__all__ = ["OcrImporter", "OcrEngine"]
