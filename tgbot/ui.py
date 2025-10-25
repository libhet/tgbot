"""Utility functions for presenting exercises and validating answers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .exercises.checker import check_answer
from .exercises.models import AnswerEvaluation, Exercise, ExerciseType


@dataclass
class RenderedExercise:
    """Rich representation that a client can render."""

    instruction: str
    context: Optional[str]
    options: Optional[List[str]]
    hints: List[str]
    expected_type: ExerciseType


class ExerciseUI:
    """High-level helpers for rendering and validating user responses."""

    def render(self, exercise: Exercise) -> RenderedExercise:
        return RenderedExercise(
            instruction=exercise.prompt.instruction,
            context=exercise.prompt.context,
            options=exercise.prompt.options,
            hints=list(exercise.prompt.hints),
            expected_type=exercise.type,
        )

    def render_form_description(self, exercise: Exercise) -> Dict[str, str]:
        if exercise.type == ExerciseType.MULTIPLE_CHOICE:
            return {
                "control": "buttons",
                "placeholder": "Выберите один из вариантов (например, A).",
            }
        if exercise.type == ExerciseType.TRUE_FALSE:
            return {
                "control": "toggle",
                "placeholder": "Укажите верно или неверно.",
            }
        return {
            "control": "text",
            "placeholder": "Введите свой ответ.",
        }

    def provide_hint(self, exercise: Exercise, attempt: int) -> Optional[str]:
        hints = exercise.prompt.hints
        if 0 <= attempt < len(hints):
            return hints[attempt]
        return None

    def evaluate(self, exercise: Exercise, answer: str | List[str]) -> AnswerEvaluation:
        return check_answer(exercise, answer)

