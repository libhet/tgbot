from __future__ import annotations

from tgnotes.services.pipeline import TextProcessingPipeline


def test_pipeline_process(sample_text: str):
    pipeline = TextProcessingPipeline()
    processed = pipeline.process(sample_text)

    assert processed.cleaned.endswith("engaging.")
    assert processed.language in {"en", "unknown"}
    assert "learning" in processed.tokens
    assert processed.lexical_units[0] == "learning"
