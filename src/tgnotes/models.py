"""Data models for notes and exercises."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass(slots=True)
class Note:
    content: str
    source_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class Exercise:
    note_id: int
    type: str
    difficulty: str
    payload: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


__all__ = ["Note", "Exercise"]
