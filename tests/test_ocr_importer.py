from __future__ import annotations

from pathlib import Path

from tgnotes.services.ocr_importer import OcrImporter


class StubEngine:
    def image_to_string(self, image) -> str:
        if isinstance(image, (bytes, bytearray)):
            return image.decode("utf-8")
        return "stubbed text"


def test_ocr_importer_with_stub(tmp_path: Path):
    image_path = tmp_path / "image.png"
    image_path.write_bytes(b"stubbed text")
    importer = OcrImporter(engine=StubEngine())
    text = importer.parse(image_path)
    assert text == "stubbed text"
