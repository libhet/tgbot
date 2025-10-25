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
from tgbot.exercises.models import ExerciseType


def test_compose_sentence_generator_creates_expected_metadata():
    generator = ComposeSentenceGenerator()
    exercise = generator.generate(
        ComposeSentenceInput(theme="travel", vocabulary=["мы", "поехали", "отдыхать"], example_structure="Мы + глагол + дополнение")
    )

    assert exercise.type is ExerciseType.COMPOSE_SENTENCE
    assert exercise.metadata["required_words"] == ["мы", "поехали", "отдыхать"]
    assert "поехали" in exercise.solution[0].lower()


def test_answer_question_generator_requires_non_empty_fields():
    generator = AnswerQuestionGenerator()
    exercise = generator.generate(
        AnswerQuestionInput(
            text="Лера готовила отчёт весь вечер.",
            question="Что делала Лера?",
            answer="готовила отчёт",
        )
    )

    assert exercise.type is ExerciseType.ANSWER_QUESTION
    assert exercise.prompt.context.startswith("Лера")


def test_multiple_choice_generator_labels_options():
    generator = MultipleChoiceGenerator()
    exercise = generator.generate(
        MultipleChoiceInput(
            question="Выберите синоним слова 'быстрый'",
            options=["скорый", "медленный", "сонный"],
            correct_index=0,
        )
    )

    assert exercise.type is ExerciseType.MULTIPLE_CHOICE
    assert exercise.prompt.options[0].startswith("A)")
    assert exercise.solution == ["A"]


def test_true_false_generator_adds_default_options():
    generator = TrueFalseGenerator()
    exercise = generator.generate(TrueFalseInput(statement="Вода закипает при 100°C", is_true=True))

    assert exercise.type is ExerciseType.TRUE_FALSE
    assert exercise.solution == ["true"]
    assert exercise.prompt.options == ["Верно", "Неверно"]

