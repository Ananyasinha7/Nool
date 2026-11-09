from datetime import date

from hypothesis import given, settings
from hypothesis import strategies as st

from backend.app.projection.project import compute_health
from backend.app.projection.types import HealthInput, StageInput
from backend.app.projection.workdays import is_working_day

TODAY = date(2026, 11, 3)


def build(rate: int, done: int) -> HealthInput:
    logs = ((date(2026, 11, 2), rate), (date(2026, 10, 31), rate), (date(2026, 10, 30), rate))
    return HealthInput("p", 5000, date(2026, 12, 20), (
        StageInput("STITCHING", date(2026, 11, 20), date(2026, 11, 1), done, logs),
        StageInput("PACKING", date(2026, 12, 15), date(2026, 11, 21), 0, ()),
    ))


@settings(max_examples=60, deadline=None)
@given(st.integers(0, 3000), st.integers(0, 4999))
def test_finish_not_before_start(rate, done):
    h = compute_health(build(rate, done), TODAY)
    assert h.projected_finish >= TODAY
    assert is_working_day(h.projected_finish)


@settings(max_examples=60, deadline=None)
@given(st.integers(1, 2000), st.integers(1, 1000), st.integers(0, 4999))
def test_higher_rate_never_finishes_later(rate, extra, done):
    slow = compute_health(build(rate, done), TODAY)
    fast = compute_health(build(rate + extra, done), TODAY)
    assert fast.projected_finish <= slow.projected_finish
