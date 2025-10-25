from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, List, Optional

from sqlalchemy.orm import Session

from . import scheduler
from .config import Settings
from .models import RepetitionHistory, Schedule
from .schemas import HistoryCreate, ScheduleCreate


class ScheduleNotFoundError(Exception):
    """Raised when a schedule is not present in the database."""


def _resolve_intervals(intervals: Optional[Iterable[int]], settings: Settings) -> List[int]:
    if intervals is None:
        return scheduler.validate_intervals(settings.default_intervals)
    return scheduler.validate_intervals(list(intervals))


def create_schedule(db: Session, payload: ScheduleCreate, settings: Settings) -> Schedule:
    intervals = _resolve_intervals(payload.intervals, settings)
    start_at = payload.start_at or datetime.utcnow()
    next_review = start_at + timedelta(days=intervals[0])
    schedule = Schedule(
        title=payload.title,
        description=payload.description,
        start_at=start_at,
        next_review_at=next_review,
        interval_index=0,
        intervals=intervals,
        active=True,
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def list_schedules(db: Session, *, active: Optional[bool] = True) -> List[Schedule]:
    query = db.query(Schedule)
    if active is not None:
        query = query.filter(Schedule.active.is_(active))
    return query.order_by(Schedule.next_review_at.asc()).all()


def _get_schedule(db: Session, schedule_id: int) -> Schedule:
    schedule = db.get(Schedule, schedule_id)
    if schedule is None:
        raise ScheduleNotFoundError
    return schedule


def get_schedule(db: Session, schedule_id: int) -> Schedule:
    return _get_schedule(db, schedule_id)


def postpone_schedule(db: Session, schedule_id: int, new_date: datetime) -> Schedule:
    schedule = _get_schedule(db, schedule_id)
    schedule.next_review_at = new_date
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def cancel_schedule(db: Session, schedule_id: int) -> None:
    schedule = _get_schedule(db, schedule_id)
    schedule.active = False
    db.add(schedule)
    db.commit()


def add_history(
    db: Session,
    schedule_id: int,
    payload: HistoryCreate,
    settings: Settings,
) -> Schedule:
    schedule = _get_schedule(db, schedule_id)
    reviewed_at = payload.reviewed_at or datetime.utcnow()
    intervals = _resolve_intervals(schedule.intervals, settings)

    next_index, next_review = scheduler.calculate_next_review(
        schedule.interval_index,
        payload.success,
        intervals,
        reviewed_at,
    )

    history = RepetitionHistory(
        schedule=schedule,
        reviewed_at=reviewed_at,
        success=payload.success,
        note=payload.note,
        interval_index=schedule.interval_index,
    )
    schedule.interval_index = next_index
    schedule.next_review_at = next_review
    db.add(history)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def get_history(db: Session, schedule_id: int) -> List[RepetitionHistory]:
    schedule = _get_schedule(db, schedule_id)
    return schedule.history
