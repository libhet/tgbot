from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class Schedule(Base):
    """Learning schedule for spaced repetition."""

    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    next_review_at = Column(DateTime, nullable=False)
    interval_index = Column(Integer, default=0, nullable=False)
    intervals = Column(JSON, nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    history = relationship(
        "RepetitionHistory",
        back_populates="schedule",
        cascade="all, delete-orphan",
        order_by="RepetitionHistory.reviewed_at",
    )


class RepetitionHistory(Base):
    """History of completed repetitions."""

    __tablename__ = "repetition_history"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False)
    reviewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    success = Column(Boolean, default=True, nullable=False)
    note = Column(Text, nullable=True)
    interval_index = Column(Integer, nullable=False)

    schedule = relationship("Schedule", back_populates="history")
