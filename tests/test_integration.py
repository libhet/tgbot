from __future__ import annotations

from pathlib import Path

from tgnotes.models import Exercise
from tgnotes.repositories import ExerciseRepository, NoteRepository
from tgnotes.services import (
    ExerciseService,
    PdfImporter,
    TextProcessingPipeline,
    WebContentImporter,
)
from tgnotes.services.ocr_importer import OcrImporter


class StubPdfBackend:
    def open(self, path: Path):
        return _StubDocument(path.read_text())


class _StubDocument:
    def __init__(self, text: str):
        self.pages = [_StubPage(text)]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _StubPage:
    def __init__(self, text: str):
        self._text = text

    def extract_text(self) -> str:
        return self._text


class StubOcrEngine:
    def image_to_string(self, image):
        if isinstance(image, (bytes, bytearray)):
            return image.decode("utf-8")
        return "Image based content"


def test_pdf_pipeline_to_exercises(tmp_path: Path, temp_database):
    pdf_path = tmp_path / "integration.pdf"
    pdf_path.write_text("Language learning with notes.")
    importer = PdfImporter(backend=StubPdfBackend())
    pipeline = TextProcessingPipeline()

    content = importer.parse(pdf_path)
    processed = pipeline.process(content)

    note_repo = NoteRepository(temp_database)
    exercise_repo = ExerciseRepository(temp_database)
    exercise_service = ExerciseService(exercise_repo)

    note = note_repo.create(content=processed.cleaned, source_type="pdf", metadata={"path": str(pdf_path)})

    move = exercise_service.create_move_words(note, processed.lexical_units, difficulty="easy")
    recall = exercise_service.create_recall_words(note, processed.lexical_units, difficulty="medium")

    assert isinstance(move, Exercise)
    assert isinstance(recall, Exercise)
    assert move.note_id == note.id
    assert "exercise_start" in recall.payload


def test_web_importer_integration(temp_database):
    def stub_fetcher(url: str, notion_api_token: str | None = None) -> str:
        return "<html><body><h1>Notion Title</h1><p>Some content.</p></body></html>"

    importer = WebContentImporter(fetcher=stub_fetcher)
    pipeline = TextProcessingPipeline()

    result = importer.fetch("https://notion.so/page", notion_api_token="secret")
    processed = pipeline.process(result.text)

    note = NoteRepository(temp_database).create(
        content=result.text, source_type="notion", metadata={"url": "https://notion.so/page"}
    )
    exercises = ExerciseService(ExerciseRepository(temp_database))
    exercise = exercises.create_recall_words(note, processed.lexical_units, difficulty="medium")

    assert exercise.metadata["words"]
    assert exercise.metadata["words"][0] == processed.lexical_units[0]


def test_image_importer_integration(tmp_path: Path, temp_database):
    image_path = tmp_path / "note.png"
    image_path.write_bytes(b"Image based content")

    importer = OcrImporter(engine=StubOcrEngine())
    pipeline = TextProcessingPipeline()

    text = importer.parse(image_path)
    processed = pipeline.process(text)

    note_repo = NoteRepository(temp_database)
    exercise_repo = ExerciseRepository(temp_database)
    exercise_service = ExerciseService(exercise_repo)

    note = note_repo.create(content=text, source_type="image", metadata={"file": str(image_path)})
    exercise = exercise_service.create_move_words(note, processed.lexical_units, difficulty="hard")

    assert exercise.note_id == note.id
    assert "Image based content" in note.content
