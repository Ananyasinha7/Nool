from datetime import date

from hypothesis import given
from hypothesis import strategies as st

from backend.app.projection.workdays import (
    add_working_days,
    is_working_day,
    next_working_day,
    working_days_between,
)


def test_sunday_is_off_saturday_is_on():
    assert not is_working_day(date(2026, 11, 1))   # Sunday
    assert is_working_day(date(2026, 11, 7))       # Saturday


def test_holiday_skipped():
    hol = {date(2026, 11, 4)}
    assert working_days_between(date(2026, 11, 3), date(2026, 11, 5), hol) == 2
    assert add_working_days(date(2026, 11, 3), 1, hol) == date(2026, 11, 5)


def test_month_end_range():
    # 30 Oct (Fri) .. 3 Nov (Tue): 30, 31, 2, 3 (1 Nov is Sunday)
    assert working_days_between(date(2026, 10, 30), date(2026, 11, 3)) == 4


def test_empty_range():
    assert working_days_between(date(2026, 11, 5), date(2026, 11, 3)) == 0


def test_add_zero_lands_on_working_day():
    assert add_working_days(date(2026, 11, 1), 0) == date(2026, 11, 2)


@given(st.dates(min_value=date(2025, 1, 1), max_value=date(2030, 1, 1)), st.integers(0, 60))
def test_add_always_working_day(d, n):
    assert is_working_day(add_working_days(d, n))
    assert next_working_day(d) >= d
