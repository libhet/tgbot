"""Text processing pipeline."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List


@dataclass(slots=True)
class ProcessedText:
    original: str
    cleaned: str
    language: str
    tokens: List[str]
    lexical_units: List[str]


class TextProcessingPipeline:
    """A pipeline performing cleaning, language detection, tokenisation and lexical extraction."""

    def clean(self, text: str) -> str:
        cleaned = re.sub(r"\s+", " ", text).strip()
        return cleaned

    def detect_language(self, text: str) -> str:
        if not text:
            return "unknown"
        latin_ratio = sum(ch.isascii() and ch.isalpha() for ch in text) / max(1, len(text))
        return "en" if latin_ratio > 0.6 else "unknown"

    def tokenize(self, text: str) -> List[str]:
        return re.findall(r"[\w']+", text.lower())

    def extract_lexical_units(self, tokens: Iterable[str]) -> List[str]:
        seen = set()
        lexical_units: List[str] = []
        for token in tokens:
            if token not in seen:
                seen.add(token)
                lexical_units.append(token)
        return lexical_units

    def process(self, text: str) -> ProcessedText:
        cleaned = self.clean(text)
        language = self.detect_language(cleaned)
        tokens = self.tokenize(cleaned)
        lexical_units = self.extract_lexical_units(tokens)
        return ProcessedText(
            original=text,
            cleaned=cleaned,
            language=language,
            tokens=tokens,
            lexical_units=lexical_units,
        )


__all__ = ["ProcessedText", "TextProcessingPipeline"]
