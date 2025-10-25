"""Handlers that orchestrate mini-app interactions and session updates."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .miniapp import FeedbackGenerator, MoveWordsState, RecallWordsConfig
from .session import Session


@dataclass
class MoveWordsResult:
    prompt: str
    keyboard: Dict[str, object]
    feedback: str


def handle_move_words_selection(
    session: Session,
    state: MoveWordsState,
    *,
    selected_word: str,
    correct_sequence: Optional[str] = None,
    hint: Optional[str] = None,
) -> MoveWordsResult:
    """Handle a ``move_words`` selection and update the session."""

    state.select_word(selected_word)
    is_correct = True
    if correct_sequence is not None:
        expected_words = [word.strip() for word in correct_sequence.split()] if correct_sequence else []
        inserted = state.inserted_words
        position = len(inserted) - 1
        if expected_words:
            try:
                expected_word = expected_words[position]
            except IndexError:
                is_correct = False
            else:
                is_correct = inserted[position] == expected_word
        else:
            is_correct = True

    if not is_correct:
        # revert the selection to mimic drag-and-drop UX where wrong word snaps back
        state.revert_selection(selected_word)

    session.record_response(
        answer={"word": selected_word, "position": len(state.inserted_words)},
        correct=is_correct,
        feedback=f"Вы выбрали: {selected_word}",
    )
    feedback = FeedbackGenerator(session).build_feedback(is_correct, hint=hint if not is_correct else None)
    keyboard_payload = {
        "inline_keyboard": state.build_keyboard(),
    }
    return MoveWordsResult(prompt=state.render_prompt(), keyboard=keyboard_payload, feedback=feedback)


@dataclass
class RecallWordsResult:
    correct: bool
    feedback: str


def handle_recall_words_submission(
    session: Session,
    config: RecallWordsConfig,
    *,
    user_answer: str,
    hint: Optional[str] = None,
) -> RecallWordsResult:
    """Validate a ``recall_words`` user submission."""

    is_correct = config.is_correct(user_answer)
    session.record_response(
        answer=user_answer,
        correct=is_correct,
        feedback="Ответ совпал" if is_correct else "Ответ не совпал",
    )
    feedback = FeedbackGenerator(session).build_feedback(is_correct, hint=None if is_correct else hint)
    return RecallWordsResult(correct=is_correct, feedback=feedback)
