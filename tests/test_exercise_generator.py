from __future__ import annotations

from tgnotes.models import Exercise, Note
from tgnotes.services.exercise_generator import ExerciseGenerator


def test_generate_move_words_payload():
    generator = ExerciseGenerator(min_words=2, max_words=4)
    payload = generator.generate_move_words(["alpha", "beta", "gamma"])

    assert payload.type == "move_words"
    assert payload.words == ["alpha", "beta", "gamma"]
    serialised = payload.serialize()
    assert serialised.startswith("type: move_words")
    assert "exercise_start" in serialised
    assert serialised.strip().endswith("exercise_end")


def test_generate_recall_words_model(sample_text: str):
    generator = ExerciseGenerator(min_words=2)
    note = Note(id=1, content=sample_text, source_type="raw", metadata={})
    payload = generator.generate_recall_words(["alpha", "beta", "gamma"])
    model = generator.as_model(note, payload, difficulty="medium", metadata={"topic": "demo"})

    assert isinstance(model, Exercise)
    assert model.type == "recall_words"
    assert "exercise_start" in model.payload
    assert model.metadata["topic"] == "demo"
    assert "alpha" in model.metadata["words"]
