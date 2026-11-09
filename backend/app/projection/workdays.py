"""Working-day calendar. Named workdays.py: calendar.py would shadow the stdlib."""
from __future__ import annotations

from collections.abc import Collection
from datetime import date, timedelta

from backend.app.config import get_config

_NO_HOLIDAYS: frozenset[date] = frozenset()


def is_working_day(d: date, holidays: Collection[date] = _NO_HOLIDAYS) -> bool:
    return d.isoweekday() in get_config().work_days and d not in holidays


def next_working_day(d: date, holidays: Collection[date] = _NO_HOLIDAYS) -> date:
    """d itself if it is a working day, otherwise the next one."""
    while not is_working_day(d, holidays):
        d += timedelta(days=1)
    return d


def add_working_days(d: date, n: int, holidays: Collection[date] = _NO_HOLIDAYS) -> date:
    """Move forward n working days from d (n=0 gives the first working day >= d)."""
    if n < 0:
        raise ValueError("n must be >= 0")
    cur = next_working_day(d, holidays) if n == 0 else d
    steps = 0
    while steps < n:
        cur += timedelta(days=1)
        if is_working_day(cur, holidays):
            steps += 1
    return cur


def working_days_between(a: date, b: date, holidays: Collection[date] = _NO_HOLIDAYS) -> int:
    """Count of working days in [a, b], both ends inclusive. 0 when b < a."""
    if b < a:
        return 0
    return sum(1 for i in range((b - a).days + 1) if is_working_day(a + timedelta(days=i), holidays))
