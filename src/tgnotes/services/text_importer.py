"""Import raw text notes."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RawTextNote:
    content: str


class TextImporter:
    """Return provided text without modification."""

    def parse(self, text: str) -> RawTextNote:
        return RawTextNote(content=text)


__all__ = ["TextImporter", "RawTextNote"]
