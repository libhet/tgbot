from __future__ import annotations

from app import models, schemas


def session_to_schema(practice_session: models.PracticeSession) -> schemas.PracticeSessionRead:
    return schemas.PracticeSessionRead(
        id=practice_session.id,
        exercise_id=practice_session.exercise_id,
        date=practice_session.date,
        status=practice_session.status,
        exercise_title=getattr(practice_session.exercise, "title", None),
    )


def exercise_to_schema(exercise: models.Exercise) -> schemas.ExerciseRead:
    sessions = [session_to_schema(session) for session in exercise.sessions]
    return schemas.ExerciseRead(
        id=exercise.id,
        title=exercise.title,
        description=exercise.description,
        type=exercise.type,
        status=exercise.status,
        sessions=sessions,
    )
