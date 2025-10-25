from dataclasses import dataclass

import pytest

from tgbot.handlers import handle_move_words_selection
from tgbot.miniapp import MoveWordsState, build_move_words_state
from tgbot.session import Session


@dataclass
class MockTelegramInlineKeyboard:
    inline_keyboard: list

    def to_dict(self):
        return {"inline_keyboard": self.inline_keyboard}


class MockTelegramMessage:
    def __init__(self) -> None:
        self.text = ""
        self.reply_markup = None
        self.feedback = None

    def edit_text(self, text: str, reply_markup: MockTelegramInlineKeyboard):
        self.text = text
        self.reply_markup = reply_markup.inline_keyboard

    def reply(self, text: str):
        self.feedback = text


@pytest.fixture
def session():
    return Session(session_id="s-move", user_id="u", task_type="move_words")


@pytest.fixture
def state():
    return build_move_words_state("Я ___ домой", ["иду", "плыву"])


def test_move_words_keyboard_updates(session, state):
    result = handle_move_words_selection(
        session,
        state,
        selected_word="иду",
        correct_sequence="иду",
    )

    assert "иду" not in state.available_words
    assert result.prompt == "Я иду домой"
    assert result.keyboard["inline_keyboard"] == [[{"text": "плыву", "callback_data": "move:плыву"}]]
    assert "Прогресс" in result.feedback


def test_move_words_sequence_validation(session):
    state = MoveWordsState(prompt_template="___ ___", available_words=["я", "иду"])

    first = handle_move_words_selection(
        session,
        state,
        selected_word="иду",
        correct_sequence="я иду",
        hint="Начните с местоимения",
    )

    assert "❌" in first.feedback
    assert session.responses[-1].correct is False

    second = handle_move_words_selection(
        session,
        state,
        selected_word="я",
        correct_sequence="я иду",
    )

    assert "✅" in second.feedback
    assert session.responses[-1].correct is True
