import pytest

from tgbot.exercises.checker import check_answer
from tgbot.exercises.generators import (
    AnswerQuestionGenerator,
    AnswerQuestionInput,
    ComposeSentenceGenerator,
    ComposeSentenceInput,
    MultipleChoiceGenerator,
    MultipleChoiceInput,
    TrueFalseGenerator,
    TrueFalseInput,
)


def test_compose_sentence_checker_requires_all_words():
    exercise = ComposeSentenceGenerator().generate(
        ComposeSentenceInput(theme="еда", vocabulary=["мы", "готовим", "ужин"])
    )

    result = check_answer(exercise, "Мы готовим вкусный ужин")
    assert result.is_correct is True

    result_missing = check_answer(exercise, "Мы готовим")
    assert result_missing.is_correct is False
    assert "все слова" in result_missing.feedback.lower()


def test_answer_question_checker_matches_normalized_answer():
    exercise = AnswerQuestionGenerator().generate(
        AnswerQuestionInput(
            text="Антон читает книгу по вечерам.",
            question="Что делает Антон вечером?",
            answer="читает книгу",
        )
    )

    result = check_answer(exercise, "Читает книгу")
    assert result.is_correct is True

    result_wrong = check_answer(exercise, "Смотрит телевизор")
    assert result_wrong.is_correct is False


def test_multiple_choice_checker_requires_single_option():
    exercise = MultipleChoiceGenerator().generate(
        MultipleChoiceInput(
            question="Столица Франции?",
            options=["Париж", "Берлин", "Рим"],
            correct_index=0,
        )
    )

    result = check_answer(exercise, "A")
    assert result.is_correct is True

    result_wrong = check_answer(exercise, "B")
    assert result_wrong.is_correct is False

    with pytest.raises(TypeError):
        check_answer(exercise, ["A", "B"])


def test_true_false_checker_normalizes_textual_responses():
    exercise = TrueFalseGenerator().generate(
        TrueFalseInput(statement="Земля вращается вокруг Солнца", is_true=True)
    )

    result = check_answer(exercise, "верно")
    assert result.is_correct is True

    result_false = check_answer(exercise, "нет")
    assert result_false.is_correct is False

