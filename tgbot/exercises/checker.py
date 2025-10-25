"""Answer verification utilities."""

from __future__ import annotations

import re
from typing import Iterable, List

from .models import AnswerEvaluation, Exercise

_WORD_RE = re.compile(r"\w+", re.UNICODE)


def _normalize(text: str) -> str:
    return " ".join(_WORD_RE.findall(text.lower()))


def _normalize_boolean(answer: str) -> str:
    truthy = {"true", "t", "yes", "y", "1", "верно", "правда"}
    falsy = {"false", "f", "no", "n", "0", "неверно", "ложь"}
    candidate = answer.strip().lower()
    if candidate in truthy:
        return "true"
    if candidate in falsy:
        return "false"
    return candidate


def _contains_all(text: str, words: Iterable[str]) -> bool:
    normalized = set(_WORD_RE.findall(text.lower()))
    return all(word.lower() in normalized for word in words)


def check_answer(exercise: Exercise, user_answer: str | List[str]) -> AnswerEvaluation:
    """Validate an answer for the provided exercise."""

    if isinstance(user_answer, list):
        normalized_answer = ", ".join(_normalize(part) for part in user_answer)
    else:
        normalized_answer = _normalize(user_answer)

    expected = [_normalize(part) for part in exercise.solution]

    if exercise.type == exercise.type.COMPOSE_SENTENCE:
        required = exercise.metadata.get("required_words", [])
        if not isinstance(user_answer, str):
            raise TypeError("Compose sentence exercises expect a textual answer.")
        missing = [word for word in required if word.lower() not in normalized_answer.split()]
        if missing:
            feedback = "Используйте все слова: " + ", ".join(missing)
            return AnswerEvaluation(False, feedback, normalized_answer, expected)
        is_correct = _contains_all(normalized_answer, required)
        feedback = (
            "Отлично! Все ключевые слова использованы."
            if is_correct
            else "Предложение не содержит всех нужных слов."
        )
        return AnswerEvaluation(is_correct, feedback, normalized_answer, expected)

    if exercise.type == exercise.type.ANSWER_QUESTION:
        if not isinstance(user_answer, str):
            raise TypeError("Answer question exercises expect a textual answer.")
        is_correct = normalized_answer in expected
        feedback = "Ответ совпал с ожидаемым." if is_correct else "Проверьте детали текста."
        return AnswerEvaluation(is_correct, feedback, normalized_answer, expected)

    if exercise.type == exercise.type.MULTIPLE_CHOICE:
        if isinstance(user_answer, list):
            raise TypeError("Multiple choice exercises expect a single option.")
        user_option = user_answer.strip().upper()
        is_correct = user_option == exercise.first_solution()
        feedback = "Правильно!" if is_correct else "Подумайте еще раз о вариантах."
        return AnswerEvaluation(is_correct, user_option, user_option, exercise.solution)

    if exercise.type == exercise.type.TRUE_FALSE:
        if isinstance(user_answer, list):
            raise TypeError("True/false exercises expect a single response.")
        normalized_bool = _normalize_boolean(user_answer)
        is_correct = normalized_bool == exercise.first_solution()
        feedback = "Верно!" if is_correct else "Сопоставьте утверждение с фактами."
        return AnswerEvaluation(is_correct, feedback, normalized_bool, exercise.solution)

    raise ValueError(f"Unsupported exercise type: {exercise.type}")

