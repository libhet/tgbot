from tgbot.exercises.generators import ComposeSentenceGenerator, ComposeSentenceInput
from tgbot.scheduler import ExerciseScheduler
from tgbot.ui import ExerciseUI


def test_ui_renders_expected_form_for_multiple_choice():
    generator = ComposeSentenceGenerator()
    exercise = generator.generate(
        ComposeSentenceInput(theme="спорт", vocabulary=["мы", "занимаемся", "йогой"], example_structure=None)
    )
    ui = ExerciseUI()

    rendered = ui.render(exercise)
    form = ui.render_form_description(exercise)

    assert rendered.instruction.startswith("Составьте предложение")
    assert form["control"] == "text"


def test_scheduler_prefers_low_score_types():
    scheduler = ExerciseScheduler()
    compose_type = scheduler.next_type()

    scheduler.register_result(compose_type, False)
    scheduler.register_result(compose_type, False)
    scheduler.register_result(compose_type, True)

    assert scheduler.next_type() == compose_type

