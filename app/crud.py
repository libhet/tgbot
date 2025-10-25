from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from . import models


def list_exercises(
    session: Session,
    *,
    status: str | None = None,
    exercise_type: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[models.Exercise]:
    stmt = select(models.Exercise).options(selectinload(models.Exercise.sessions)).order_by(models.Exercise.id)
    if status:
        stmt = stmt.where(models.Exercise.status == status)
    if exercise_type:
        stmt = stmt.where(models.Exercise.type == exercise_type)
    if date_from or date_to:
        stmt = stmt.join(models.Exercise.sessions)
        if date_from:
            stmt = stmt.where(models.PracticeSession.date >= date_from)
        if date_to:
            stmt = stmt.where(models.PracticeSession.date <= date_to)
    result = session.scalars(stmt).unique().all()
    return result


def list_calendar_days(
    session: Session,
    *,
    status: str | None = None,
    exercise_type: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[models.PracticeSession]:
    stmt = select(models.PracticeSession).options(selectinload(models.PracticeSession.exercise)).order_by(models.PracticeSession.date)
    if date_from:
        stmt = stmt.where(models.PracticeSession.date >= date_from)
    if date_to:
        stmt = stmt.where(models.PracticeSession.date <= date_to)
    if status:
        stmt = stmt.where(models.PracticeSession.status == status)
    if exercise_type:
        stmt = stmt.join(models.PracticeSession.exercise).where(
            models.Exercise.type == exercise_type
        )
    else:
        stmt = stmt.join(models.PracticeSession.exercise)
    return session.scalars(stmt).unique().all()


def create_sample_data(session: Session) -> None:
    if session.query(models.Exercise).count() > 0:
        return

    breathing = models.Exercise(
        title="Breathing Control",
        description="Improve lung capacity with controlled breathing.",
        type="warmup",
        status="published",
    )
    scales = models.Exercise(
        title="Chromatic Scales",
        description="Run through chromatic scales for 10 minutes.",
        type="technique",
        status="published",
    )
    repertoire = models.Exercise(
        title="Sonata Practice",
        description="Work on the first movement of the sonata.",
        type="repertoire",
        status="draft",
    )
    session.add_all([breathing, scales, repertoire])
    session.flush()

    session.add_all(
        [
            models.PracticeSession(
                exercise_id=breathing.id, date=date.today(), status="completed"
            ),
            models.PracticeSession(
                exercise_id=scales.id, date=date.today(), status="planned"
            ),
            models.PracticeSession(
                exercise_id=repertoire.id, date=date.today().replace(day=1), status="planned"
            ),
        ]
    )
    session.commit()
