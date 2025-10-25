from __future__ import annotations

from typing import List

from fastapi import Depends, FastAPI, HTTPException, Response, status

from .config import Settings, get_settings
from .crud import (
    ScheduleNotFoundError,
    add_history,
    cancel_schedule,
    create_schedule,
    get_history,
    get_schedule,
    list_schedules,
    postpone_schedule,
)
from .database import Base, engine, get_db
from .schemas import HistoryCreate, HistoryRead, ScheduleCreate, ScheduleRead, ScheduleReschedule


app = FastAPI(title="Spaced Repetition Planner", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/schedules", response_model=List[ScheduleRead])
def read_schedules(
    active: bool | None = True,
    db=Depends(get_db),
) -> List[ScheduleRead]:
    schedules = list_schedules(db, active=active)
    return schedules


@app.post("/schedules", response_model=ScheduleRead, status_code=status.HTTP_201_CREATED)
def create_schedule_endpoint(
    payload: ScheduleCreate,
    db=Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ScheduleRead:
    schedule = create_schedule(db, payload, settings)
    return schedule


@app.get("/schedules/{schedule_id}", response_model=ScheduleRead)
def read_schedule(schedule_id: int, db=Depends(get_db)) -> ScheduleRead:
    try:
        return get_schedule(db, schedule_id)
    except ScheduleNotFoundError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found") from exc


@app.post("/schedules/{schedule_id}/reschedule", response_model=ScheduleRead)
def reschedule_schedule(
    schedule_id: int,
    payload: ScheduleReschedule,
    db=Depends(get_db),
) -> ScheduleRead:
    try:
        return postpone_schedule(db, schedule_id, payload.next_review_at)
    except ScheduleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found") from exc


@app.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_schedule_endpoint(schedule_id: int, db=Depends(get_db)) -> Response:
    try:
        cancel_schedule(db, schedule_id)
    except ScheduleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/schedules/{schedule_id}/history", response_model=ScheduleRead)
def add_history_endpoint(
    schedule_id: int,
    payload: HistoryCreate,
    db=Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ScheduleRead:
    try:
        return add_history(db, schedule_id, payload, settings)
    except ScheduleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found") from exc


@app.get("/schedules/{schedule_id}/history", response_model=List[HistoryRead])
def read_history(schedule_id: int, db=Depends(get_db)) -> List[HistoryRead]:
    try:
        return get_history(db, schedule_id)
    except ScheduleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found") from exc
