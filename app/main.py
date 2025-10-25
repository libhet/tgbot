from __future__ import annotations

from collections import defaultdict
from datetime import date

from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session

from . import crud, models, schemas, serializers
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Practice Planner API")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def create_seed_data() -> None:
    with SessionLocal() as db:
        crud.create_sample_data(db)


@app.get("/api/exercises", response_model=list[schemas.ExerciseRead])
def get_exercises(
    *,
    status: str | None = Query(default=None),
    type: str | None = Query(default=None, alias="exercise_type"),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[schemas.ExerciseRead]:
    exercises = crud.list_exercises(
        db,
        status=status,
        exercise_type=type,
        date_from=date_from,
        date_to=date_to,
    )
    return [serializers.exercise_to_schema(exercise) for exercise in exercises]


@app.get("/api/calendar", response_model=list[schemas.CalendarDay])
def get_calendar(
    *,
    status: str | None = Query(default=None),
    type: str | None = Query(default=None, alias="exercise_type"),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[schemas.CalendarDay]:
    sessions = crud.list_calendar_days(
        db,
        status=status,
        exercise_type=type,
        date_from=date_from,
        date_to=date_to,
    )
    buckets: dict[date, list[schemas.PracticeSessionRead]] = defaultdict(list)
    for practice_session in sessions:
        day = practice_session.date
        buckets[day].append(serializers.session_to_schema(practice_session))
    return [
        schemas.CalendarDay(date=day, sessions=sessions)
        for day, sessions in sorted(buckets.items())
    ]
