import pytest

from tgbot.handlers import handle_recall_words_submission
from tgbot.miniapp import RecallWordsConfig
from tgbot.session import Session


def test_recall_words_case_insensitive():
    session = Session(session_id="s-recall", user_id="u", task_type="recall_words")
    config = RecallWordsConfig.from_answer("Python", alternatives=["Питон"])  # alternative transliteration

    result = handle_recall_words_submission(
        session,
        config,
        user_answer="python",
    )

    assert result.correct is True
    assert "✅" in result.feedback
    assert session.status.name == "COMPLETED"


def test_recall_words_with_hint():
    session = Session(session_id="s-recall-2", user_id="u", task_type="recall_words")
    config = RecallWordsConfig.from_answer("Python")

    result = handle_recall_words_submission(
        session,
        config,
        user_answer="java",
        hint="Язык, созданный Гвидо",
    )

    assert result.correct is False
    assert "❌" in result.feedback
    assert "Гвидо" in result.feedback
    assert session.status.name == "ACTIVE"
