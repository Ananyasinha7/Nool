"""Worked examples from Doc3 section 7 (demo date Tue 3 Nov 2026) plus edge cases."""
from datetime import date, timedelta

import pytest

from backend.app.projection.project import compute_health
from backend.app.projection.types import HealthInput, StageInput

TODAY = date(2026, 11, 3)


def d(day: int, month: int = 11) -> date:
    return date(2026, month, day)


def full(key: str, qty: int, deadline: date) -> StageInput:
    return StageInput(key, deadline, deadline - timedelta(days=8), qty, ())


def logs_latest_first(qtys: list[int], last: date) -> tuple[tuple[date, int], ...]:
    out, cur = [], last
    for q in qtys:
        while cur.isoweekday() == 7:
            cur -= timedelta(days=1)
        out.append((cur, q))
        cur -= timedelta(days=1)
    return tuple(out)


def order_88213() -> HealthInput:
    ex = d(20)
    return HealthInput("88213", 12000, ex, (
        full("CUTTING", 12000, d(27, 10)),
        StageInput("STITCHING", d(13), d(28, 10), 6800, logs_latest_first([490, 480, 465], d(2))),
        StageInput("FINISHING", d(17), d(14), 0, ()),
        StageInput("PACKING", d(18), d(17), 0, ()),
    ))


def order_88240() -> HealthInput:
    return HealthInput("88240", 8000, d(12), (
        full("CUTTING", 8000, d(19, 10)),
        full("STITCHING", 8000, d(26, 10)),
        StageInput("FINISHING", d(9), d(27, 10), 5200, logs_latest_first([290, 310, 305], d(2))),
        StageInput("PACKING", d(10), d(10), 0, ()),
    ))


def order_0488() -> HealthInput:
    return HealthInput("0488", 10000, d(28), (
        full("CUTTING", 10000, d(4, 11) - timedelta(days=10)),
        StageInput("PRINTING", d(12), d(27, 10), 3100,
                   logs_latest_first([810, 790, 800], d(2))),
        StageInput("STITCHING", d(21), d(13), 0, ()),
        StageInput("FINISHING", d(25), d(22), 0, ()),
        StageInput("PACKING", d(26), d(26), 0, ()),
    ))


def test_88213_amber():
    h = compute_health(order_88213(), TODAY)
    assert h.health == "AMBER"
    assert h.working_days_left == 10
    assert h.required_per_day == pytest.approx(520)
    assert h.actual_per_day == pytest.approx(482.5)
    assert h.ratio == pytest.approx(0.928, abs=0.001)
    assert h.projected_finish == d(14)
    assert h.stage_slip_days == 1
    assert h.projected_ship_date == d(19)
    assert h.ship_slip_days == 0


def test_88240_red():
    h = compute_health(order_88240(), TODAY)
    assert h.health == "RED"
    assert h.working_days_left == 6
    assert h.required_per_day == pytest.approx(466.67, abs=0.01)
    assert h.actual_per_day == pytest.approx(299.17, abs=0.01)
    assert h.projected_finish == d(13)
    assert h.stage_slip_days == 4
    assert h.projected_ship_date == d(16)
    assert h.ship_slip_days == 3
    assert h.recovery_per_day == 168


def test_0488_green():
    h = compute_health(order_0488(), TODAY)
    assert h.health == "GREEN"
    assert h.working_days_left == 9
    assert h.required_per_day == pytest.approx(766.67, abs=0.01)
    assert h.actual_per_day == pytest.approx(801.67, abs=0.01)
    assert h.projected_finish == d(12)
    assert h.stage_slip_days == 0


def test_no_logs_is_low_confidence_planned_rate():
    inp = HealthInput("x", 1000, d(28), (
        StageInput("CUTTING", d(20), d(4), 0, ()),
    ))
    h = compute_health(inp, TODAY)
    assert h.low_confidence and h.actual_per_day > 0 and not h.stale


def test_single_log_only():
    inp = HealthInput("x", 1000, d(28), (
        StageInput("CUTTING", d(20), d(4), 100, ((d(2), 100),)),
    ))
    h = compute_health(inp, TODAY)
    assert h.actual_per_day == 100 and not h.low_confidence


def test_stale_green_becomes_grey_but_never_masks_red():
    stale_logs = ((date(2026, 10, 28), 500),)
    ok = HealthInput("g", 1000, d(30), (StageInput("CUTTING", d(28), d(1, 10), 500, stale_logs),))
    h = compute_health(ok, TODAY)
    assert h.stale and h.health == "GREY"
    bad = HealthInput("r", 100000, d(30), (StageInput("CUTTING", d(10), d(1, 10), 500, stale_logs),))
    assert compute_health(bad, TODAY).health == "RED"


def test_log_today_shifts_start():
    base = StageInput("CUTTING", d(10), d(1), 100, ((TODAY, 100),))
    h = compute_health(HealthInput("x", 1000, d(20), (base,)), TODAY)
    # 4 Nov..10 Nov working days = 4,5,6,7,9,10 -> 6 (today not counted)
    assert h.working_days_left == 6


def test_overdue_stage():
    inp = HealthInput("x", 1000, d(20), (StageInput("CUTTING", d(2), d(1, 10), 100, ((d(2), 100),)),))
    h = compute_health(inp, TODAY)
    assert h.overdue and h.required_per_day is None and h.health == "RED"


def test_complete_order():
    inp = HealthInput("x", 1000, d(20), (StageInput("PACKING", d(18), d(10), 1000, ()),))
    h = compute_health(inp, TODAY)
    assert h.active_stage is None and h.health == "GREEN"


def test_zero_rate_does_not_divide_by_zero():
    inp = HealthInput("x", 1000, d(28), (
        StageInput("CUTTING", d(20), d(4), 0, ((d(2), 0), (d(1, 10), 0))),
    ))
    h = compute_health(inp, TODAY)
    assert h.health == "RED" and h.projected_finish > d(20)


def test_holiday_skipped():
    hol = frozenset({d(4)})
    base = StageInput("CUTTING", d(6), d(1), 0, ((d(2), 100),))
    h = compute_health(HealthInput("x", 1000, d(20), (base,), hol), TODAY)
    assert h.working_days_left == 3  # 3, 5, 6


def test_slack_absorbs_slip_downstream():
    assert compute_health(order_88213(), TODAY).ship_slip_days == 0


@pytest.mark.parametrize(
    "ratio,expected", [(1.0, "GREEN"), (0.9999, "AMBER"), (0.8, "AMBER"), (0.7999, "RED")]
)
def test_ratio_boundaries(ratio, expected):
    # Tested on the status function: end-to-end, slip would also move the colour.
    from backend.app.projection.status import ratio_status
    assert ratio_status(ratio) == expected


@pytest.mark.parametrize("slip,expected", [(0, "GREEN"), (1, "AMBER"), (2, "AMBER"), (3, "RED")])
def test_slip_boundaries(slip, expected):
    from backend.app.projection.status import slip_status
    assert slip_status(slip) == expected
