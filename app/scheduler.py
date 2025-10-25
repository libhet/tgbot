from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, List, Sequence


def validate_intervals(intervals: Sequence[int]) -> List[int]:
    """Ensure intervals are positive integers."""

    if not intervals:
        raise ValueError("Intervals list cannot be empty")
    normalized = []
    for interval in intervals:
        if interval <= 0:
            raise ValueError("Intervals must be positive integers")
        normalized.append(int(interval))
    return normalized


def generate_review_dates(start_at: datetime, intervals: Iterable[int]) -> List[datetime]:
    """Generate review dates based on start moment and intervals."""

    base = start_at
    dates: List[datetime] = []
    for days in intervals:
        base = base + timedelta(days=int(days))
        dates.append(base)
    return dates


def get_next_interval_index(current_index: int, success: bool, intervals: Sequence[int]) -> int:
    """Return the next interval index based on review result."""

    if success:
        return min(current_index + 1, len(intervals) - 1)
    return 0


def calculate_next_review(
    current_index: int,
    success: bool,
    intervals: Sequence[int],
    reference: datetime,
) -> tuple[int, datetime]:
    """Calculate next review index and datetime."""

    validated = validate_intervals(intervals)
    next_index = get_next_interval_index(current_index, success, validated)
    next_date = reference + timedelta(days=validated[next_index])
    return next_index, next_date
