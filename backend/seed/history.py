"""Daily-log history generator. Sums are exact, the last logged days are controlled so the
weighted run-rate lands on each order's target status (Doc3 section 13)."""
from __future__ import annotations

import math
from datetime import date, timedelta

from backend.app.projection.workdays import is_working_day

HISTORY_START = date(2026, 10, 12)


def working_days(a: date, b: date, holidays: frozenset[date]) -> list[date]:
    out, cur = [], a
    while cur <= b:
        if is_working_day(cur, holidays):
            out.append(cur)
        cur += timedelta(days=1)
    return out


def _split(total: int, n: int, ramp: bool = True) -> list[int]:
    """Split total into n non-negative ints summing exactly; ramp gives later days more."""
    if n <= 0:
        return []
    weights = [1 + 0.04 * i for i in range(n)] if ramp else [1.0] * n
    parts = [int(total * w / sum(weights)) for w in weights]
    parts[0] += total - sum(parts)  # remainder to the earliest day so the sum is exact
    return parts


def active_stage_logs(days: list[date], done: int, last_latest_first: list[int]) -> list[tuple[date, int]]:
    """days: ascending candidate dates; returns (date, qty) pairs summing to done."""
    if done <= 0 or not days:
        return []
    tail = list(reversed(last_latest_first))  # chronological
    if sum(tail) > done:
        # Too few pieces made for that many days at the target rate: spread over fewer days.
        r = max(1, max(tail))
        k = max(1, min(len(days), round(done / r)))
        return list(zip(days[-k:], _split(done, k, ramp=False), strict=True))
    rest = done - sum(tail)
    earlier_days = days[: len(days) - len(tail)]
    avg = max(1, sum(tail) / len(tail))
    k = min(len(earlier_days), math.ceil(rest / avg)) if rest else 0
    chosen = earlier_days[len(earlier_days) - k:] if k else []
    qtys = _split(rest, k)
    # Keep every earlier day below the recent level so the trend looks plausible.
    return list(zip(chosen, qtys, strict=True)) + list(zip(days[len(days) - len(tail):], tail, strict=True))


def completed_stage_logs(
    qty: int, end_before: date, holidays: frozenset[date], n_days: int = 4
) -> list[tuple[date, int]]:
    """n_days working days ending strictly before end_before, summing to qty."""
    out, cur = [], end_before - timedelta(days=1)
    while len(out) < n_days:
        if is_working_day(cur, holidays):
            out.append(cur)
        cur -= timedelta(days=1)
    out.reverse()
    return list(zip(out, _split(qty, n_days, ramp=False), strict=True))
