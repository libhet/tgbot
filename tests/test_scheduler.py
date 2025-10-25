from datetime import datetime

import pytest

from app.scheduler import calculate_next_review, generate_review_dates, validate_intervals


def test_generate_review_dates_produces_expected_sequence():
    start = datetime(2024, 1, 1, 8, 0, 0)
    intervals = [1, 3, 7]

    result = generate_review_dates(start, intervals)

    assert result == [
        datetime(2024, 1, 2, 8, 0, 0),
        datetime(2024, 1, 5, 8, 0, 0),
        datetime(2024, 1, 12, 8, 0, 0),
    ]


def test_calculate_next_review_handles_success_and_failure():
    reference = datetime(2024, 1, 10, 8, 0, 0)
    intervals = [1, 3, 7]

    next_index, next_review = calculate_next_review(0, True, intervals, reference)
    assert next_index == 1
    assert next_review == datetime(2024, 1, 13, 8, 0, 0)

    next_index, next_review = calculate_next_review(2, False, intervals, reference)
    assert next_index == 0
    assert next_review == datetime(2024, 1, 11, 8, 0, 0)


def test_validate_intervals_rejects_invalid_values():
    with pytest.raises(ValueError):
        validate_intervals([])
    with pytest.raises(ValueError):
        validate_intervals([0, 1, 2])
