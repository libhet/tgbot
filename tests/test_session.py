from datetime import datetime

from tgbot.session import Session, SessionStatus


def test_session_serialization_roundtrip():
    session = Session(session_id="s1", user_id="u1", task_type="move_words")
    session.record_response(answer={"word": "привет"}, correct=True)
    payload = session.to_json()

    restored = Session.from_json(payload)

    assert restored.session_id == "s1"
    assert restored.user_id == "u1"
    assert restored.task_type == "move_words"
    assert restored.status == SessionStatus.COMPLETED
    assert restored.responses[0].answer == {"word": "привет"}
    assert isinstance(restored.started_at, datetime)


def test_session_progress_computation():
    session = Session(session_id="s2", user_id="u1", task_type="recall_words")
    session.record_response(answer="one", correct=True)
    session.record_response(answer="two", correct=False)

    assert session.progress() == 0.5
    summary = session.summary()
    assert summary == {
        "status": "active",
        "completed_steps": 1,
        "total_steps": 2,
        "progress": 0.5,
    }
