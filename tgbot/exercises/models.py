"""Domain models shared by exercise components."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional


class ExerciseType(str, Enum):
    """Enumerates supported exercise formats."""

    COMPOSE_SENTENCE = "compose_sentence"
    ANSWER_QUESTION = "answer_question"
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"

    @classmethod
    def from_storage_key(cls, key: str) -> "ExerciseType":
        try:
            return cls(key)
        except ValueError as exc:
            raise ValueError(f"Unsupported exercise type '{key}'") from exc


@dataclass(frozen=True)
class ExercisePrompt:
    """Display information for an exercise."""

    instruction: str
    context: Optional[str] = None
    options: Optional[List[str]] = None
    hints: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class Exercise:
    """Fully-specified exercise to present to a learner."""

    type: ExerciseType
    prompt: ExercisePrompt
    solution: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def expects_multiple_answers(self) -> bool:
        return bool(self.metadata.get("allow_multiple", False))

    def first_solution(self) -> str:
        return self.solution[0]


@dataclass(frozen=True)
class AnswerEvaluation:
    """Represents the result of verifying a user's answer."""

    is_correct: bool
    feedback: str
    normalized_answer: str
    expected: Iterable[str]

