"""UI scenario tests using Telegram-like mocks."""
from dataclasses import dataclass

from tgbot.handlers import handle_move_words_selection, handle_recall_words_submission
from tgbot.miniapp import MoveWordsState, RecallWordsConfig
from tgbot.session import Session


@dataclass
class MockCallbackQuery:
    data: str
    message: "MockMessage"


class MockMessage:
    def __init__(self) -> None:
        self.last_text = None
        self.last_markup = None
        self.last_feedback = None

    def edit_text(self, text, reply_markup):
        self.last_text = text
        self.last_markup = reply_markup

    def answer(self, text):
        self.last_feedback = text


def test_move_words_ui_flow():
    session = Session(session_id="ui1", user_id="user1", task_type="move_words")
    state = MoveWordsState(prompt_template="___ кот", available_words=["черный", "белый"])
    message = MockMessage()
    query = MockCallbackQuery(data="move:черный", message=message)

    result = handle_move_words_selection(
        session,
        state,
        selected_word=query.data.split(":")[1],
        correct_sequence="черный",
    )

    message.edit_text(result.prompt, result.keyboard)
    message.answer(result.feedback)

    assert message.last_text == "черный кот"
    assert message.last_markup == {"inline_keyboard": [[{"text": "белый", "callback_data": "move:белый"}]]}
    assert "Прогресс" in message.last_feedback


def test_recall_words_ui_flow():
    session = Session(session_id="ui2", user_id="user1", task_type="recall_words")
    config = RecallWordsConfig.from_answer("telegram", alternatives=["телеграм"], case_sensitive=False)
    message = MockMessage()

    result = handle_recall_words_submission(
        session,
        config,
        user_answer="Телеграм",
    )
    message.answer(result.feedback)

    assert session.status.name == "COMPLETED"
    assert "✅" in message.last_feedback
