"""Interactive mini-app mechanics for Telegram word training tasks."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from .session import Session


@dataclass
class MoveWordsState:
    """Holds state for the ``move_words`` training interaction."""

    prompt_template: str
    available_words: List[str]
    inserted_words: List[str] = field(default_factory=list)

    def render_prompt(self) -> str:
        """Return the current prompt with placeholders substituted."""

        prompt = self.prompt_template
        for word in self.inserted_words:
            prompt = prompt.replace("___", word, 1)
        return prompt

    def build_keyboard(self) -> List[List[Dict[str, str]]]:
        """Return inline keyboard payload resembling Telegram format."""

        rows: List[List[Dict[str, str]]] = []
        for word in self.available_words:
            rows.append([
                {
                    "text": word,
                    "callback_data": f"move:{word}",
                }
            ])
        return rows

    def select_word(self, word: str) -> None:
        """Select a word and move it from the available list into the prompt."""

        if word not in self.available_words:
            raise ValueError(f"Word '{word}' is not available for selection")
        self.available_words.remove(word)
        self.inserted_words.append(word)

    def revert_selection(self, word: str) -> None:
        """Undo the latest selection by returning the word back to the cloud."""

        if not self.inserted_words or self.inserted_words[-1] != word:
            raise ValueError("Only the most recent selection can be reverted")
        self.inserted_words.pop()
        self.available_words.append(word)

    def next_placeholder_exists(self) -> bool:
        """Return whether the prompt still contains placeholders."""

        return "___" in self.render_prompt()


def build_move_words_state(prompt_template: str, words: Iterable[str]) -> MoveWordsState:
    """Convenience factory for :class:`MoveWordsState`."""

    return MoveWordsState(prompt_template=prompt_template, available_words=list(words))


@dataclass
class RecallWordsConfig:
    """Configuration for ``recall_words`` interactions."""

    expected_answers: List[str]
    case_sensitive: bool = False

    def normalize(self, answer: str) -> str:
        return answer if self.case_sensitive else answer.casefold()

    def is_correct(self, answer: str) -> bool:
        normalized_answer = self.normalize(answer.strip())
        return any(self.normalize(expected) == normalized_answer for expected in self.expected_answers)

    @classmethod
    def from_answer(cls, answer: str, *, alternatives: Optional[Iterable[str]] = None, case_sensitive: bool = False) -> "RecallWordsConfig":
        answers = [answer]
        if alternatives:
            answers.extend(alternatives)
        return cls(expected_answers=list(answers), case_sensitive=case_sensitive)


class FeedbackGenerator:
    """Produces user-facing feedback messages and progress updates."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def build_feedback(self, correct: bool, *, hint: Optional[str] = None) -> str:
        progress = int(self.session.progress() * 100)
        status_line = "✅ Правильно!" if correct else "❌ Ошибка."
        hint_line = f"\nПодсказка: {hint}" if hint else ""
        return f"{status_line}\nПрогресс: {progress}%{hint_line}"


__all__ = [
    "MoveWordsState",
    "RecallWordsConfig",
    "FeedbackGenerator",
    "build_move_words_state",
]
