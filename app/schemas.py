from __future__ import annotations

from datetime import date
from typing import List

from pydantic import BaseModel, Field


class PracticeSessionBase(BaseModel):
    date: date
    status: str = Field(default="planned")


class PracticeSessionCreate(PracticeSessionBase):
    exercise_id: int


class PracticeSessionRead(PracticeSessionBase):
    id: int
    exercise_id: int
    exercise_title: str | None = None

    class Config:
        from_attributes = True


class ExerciseBase(BaseModel):
    title: str
    description: str | None = None
    type: str
    status: str = Field(default="draft")


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseRead(ExerciseBase):
    id: int
    sessions: List[PracticeSessionRead] = Field(default_factory=list)

    class Config:
        from_attributes = True


class CalendarDay(BaseModel):
    date: date
    sessions: List[PracticeSessionRead]
