"""Exercise generators that assemble prompts and expected answers."""

from __future__ import annotations

import random
from dataclasses import dataclass
from textwrap import fill
from typing import Iterable, List, Sequence

from .models import Exercise, ExercisePrompt, ExerciseType


@dataclass
class ComposeSentenceInput:
    theme: str
    vocabulary: Sequence[str]
    example_structure: str | None = None


class ComposeSentenceGenerator:
    """Creates sentence-building exercises for a given theme."""

    def generate(self, data: ComposeSentenceInput) -> Exercise:
        if not data.vocabulary:
            raise ValueError("Vocabulary is required to compose a sentence.")

        instruction = (
            "Составьте предложение по теме \"{theme}\" используя следующие слова: "
            "{words}."
        ).format(theme=data.theme, words=", ".join(data.vocabulary))

        hints: List[str] = [
            "Используйте все предложенные слова хотя бы один раз.",
            "Соблюдайте базовый порядок слов: подлежащее — сказуемое — дополнение.",
        ]
        if data.example_structure:
            hints.append(f"Ориентируйтесь на структуру: {data.example_structure}")

        example_sentence = self._build_example(data.vocabulary, data.theme)
        prompt = ExercisePrompt(
            instruction=instruction,
            context=f"Тема: {data.theme}",
            hints=hints,
        )
        return Exercise(
            type=ExerciseType.COMPOSE_SENTENCE,
            prompt=prompt,
            solution=[example_sentence],
            metadata={"required_words": list(data.vocabulary)},
        )

    @staticmethod
    def _build_example(vocabulary: Sequence[str], theme: str) -> str:
        subject = vocabulary[0].capitalize()
        rest = " ".join(vocabulary[1:]) if len(vocabulary) > 1 else ""
        sentence = f"{subject} {rest}".strip()
        if not sentence.endswith("."):
            sentence += "."
        return fill(sentence + f" ({theme})")


@dataclass
class AnswerQuestionInput:
    text: str
    question: str
    answer: str


class AnswerQuestionGenerator:
    """Creates question-answer exercises based on a source text."""

    def generate(self, data: AnswerQuestionInput) -> Exercise:
        if not data.text.strip():
            raise ValueError("A source text is required to generate questions.")
        if not data.question.strip():
            raise ValueError("The question must not be empty.")
        if not data.answer.strip():
            raise ValueError("An expected answer must be provided.")

        prompt = ExercisePrompt(
            instruction=data.question.strip(),
            context=data.text.strip(),
            hints=["Найдите предложение, которое напрямую отвечает на вопрос."],
        )
        return Exercise(
            type=ExerciseType.ANSWER_QUESTION,
            prompt=prompt,
            solution=[data.answer.strip()],
        )


@dataclass
class MultipleChoiceInput:
    question: str
    options: List[str]
    correct_index: int


class MultipleChoiceGenerator:
    """Generates multiple-choice exercises with labeled options."""

    def generate(self, data: MultipleChoiceInput) -> Exercise:
        if len(data.options) < 2:
            raise ValueError("At least two options are required for multiple choice exercises.")
        if not 0 <= data.correct_index < len(data.options):
            raise ValueError("Correct index is out of range for provided options.")

        labels = [chr(ord("A") + idx) for idx in range(len(data.options))]
        labeled_options = [f"{label}) {option}" for label, option in zip(labels, data.options)]
        prompt = ExercisePrompt(
            instruction=data.question.strip(),
            options=labeled_options,
            hints=["Внимательно сравните все варианты перед выбором."],
        )
        return Exercise(
            type=ExerciseType.MULTIPLE_CHOICE,
            prompt=prompt,
            solution=[labels[data.correct_index]],
            metadata={"options": labeled_options},
        )


@dataclass
class TrueFalseInput:
    statement: str
    is_true: bool
    rationale: str | None = None


class TrueFalseGenerator:
    """Builds true/false exercises with optional rationale for hints."""

    def generate(self, data: TrueFalseInput) -> Exercise:
        if not data.statement.strip():
            raise ValueError("Statement is required for true/false exercises.")

        hints = ["Подумайте, подтверждается ли утверждение исходными материалами."]
        if data.rationale:
            hints.append(f"Подсказка: {data.rationale.strip()}")

        prompt = ExercisePrompt(
            instruction=f"Верно ли утверждение: {data.statement.strip()}?",
            hints=hints,
            options=["Верно", "Неверно"],
        )
        answer = "true" if data.is_true else "false"
        return Exercise(
            type=ExerciseType.TRUE_FALSE,
            prompt=prompt,
            solution=[answer],
        )


def choose_generator(types: Iterable[ExerciseType]) -> ExerciseType:
    """Select a generator type at random from the provided options."""

    options = list(types)
    if not options:
        raise ValueError("At least one exercise type must be provided.")
    return random.choice(options)

