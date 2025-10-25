from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ScheduleBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    intervals: Optional[List[int]] = Field(
        default=None,
        description="Custom spaced repetition intervals in days.",
    )


class ScheduleCreate(ScheduleBase):
    start_at: Optional[datetime] = Field(
        default=None,
        description="Moment when the learner starts the repetition sequence.",
    )


class ScheduleRead(ScheduleBase):
    id: int
    start_at: datetime
    created_at: datetime
    next_review_at: datetime
    interval_index: int
    intervals: List[int]
    active: bool

    model_config = ConfigDict(from_attributes=True)


class ScheduleReschedule(BaseModel):
    next_review_at: datetime = Field(..., description="New review date.")


class HistoryCreate(BaseModel):
    success: bool
    reviewed_at: Optional[datetime] = None
    note: Optional[str] = None


class HistoryRead(HistoryCreate):
    id: int
    schedule_id: int
    interval_index: int

    model_config = ConfigDict(from_attributes=True)
