"""compute_health: the product's core (Doc3 section 7). Pure, no I/O."""
from __future__ import annotations

import math
from datetime import date, timedelta

from backend.app.config import get_config
from backend.app.projection.rate import weighted_rate
from backend.app.projection.status import combine
from backend.app.projection.types import HealthInput, OrderHealthResult, StageInput
from backend.app.projection.workdays import (
    add_working_days,
    is_working_day,
    working_days_between,
)

MAX_FINISH_WD = 365  # cap used when the rate is zero (avoids division by zero)


def _slip(deadline: date, finish: date, holidays: frozenset[date]) -> int:
    """Working days strictly after deadline up to and including finish."""
    if finish <= deadline:
        return 0
    return working_days_between(deadline + timedelta(days=1), finish, holidays)


def _recent_rates(stage: StageInput, today: date, holidays: frozenset[date]) -> list[int]:
    # Only working days up to today; latest first (weights apply latest first).
    eligible = [(d, q) for d, q in stage.logs if d <= today and is_working_day(d, holidays)]
    eligible.sort(key=lambda x: x[0], reverse=True)
    return [q for _, q in eligible]


def compute_health(inp: HealthInput, today: date) -> OrderHealthResult:
    cfg = get_config()
    hol = inp.holidays
    lead_days = (inp.ex_factory - today).days

    active = next((s for s in inp.stages if s.done < inp.qty), None)
    if active is None:
        last = inp.stages[-1] if inp.stages else None
        return OrderHealthResult(
            order_id=inp.order_id, health="GREEN", active_stage=None, qty=inp.qty,
            done=inp.qty, remaining=0, required_per_day=None, actual_per_day=0.0,
            working_days_left=0, overdue=False,
            stage_deadline=last.deadline if last else inp.ex_factory,
            projected_finish=today, stage_slip_days=0, projected_ship_date=inp.ex_factory,
            ship_slip_days=0, projected_at_deadline=inp.qty, ratio=1.0,
            low_confidence=False, stale=False, last_log_date=None,
            lead_days=lead_days, recovery_per_day=0,
        )

    # Step 1: count today only if nothing is logged for it yet.
    logged_today = any(d == today for d, _ in active.logs)
    start = today if not logged_today else today + timedelta(days=1)

    remaining = inp.qty - active.done
    days_left = working_days_between(start, active.deadline, hol)
    overdue = days_left <= 0

    # Step 5: run-rate, or the planned rate when nothing has been logged.
    recent = _recent_rates(active, today, hol)
    low_confidence = not recent
    if recent:
        actual = weighted_rate(recent)
    else:
        window = max(1, working_days_between(active.window_start, active.deadline, hol))
        actual = inp.qty / window

    required: float | None = None if overdue else remaining / days_left
    ratio = 0.0 if overdue or required is None else actual / required

    if actual > 0:
        finish_days = math.ceil(remaining / actual)
    else:
        finish_days = MAX_FINISH_WD
    finish_days = min(max(finish_days, 1), MAX_FINISH_WD)
    finish = add_working_days(start, finish_days - 1, hol)
    stage_slip = _slip(active.deadline, finish, hol)

    at_deadline = min(inp.qty, int(round(active.done + actual * max(days_left, 0))))

    # Step 8: later stages start only after the previous one finishes (plus lag).
    idx = inp.stages.index(active)
    prev_finish = finish
    for s in inp.stages[idx + 1:]:
        prev_finish = max(s.deadline, add_working_days(prev_finish, cfg.stage_lag_wd, hol))
    ship = add_working_days(prev_finish, cfg.inspection_wd, hol)
    ship_slip = _slip(inp.ex_factory, ship, hol)

    # Step 9: stale when the active stage has been silent too long.
    last_log = max((d for d, _ in active.logs if d <= today), default=None)
    stale = False
    if last_log is not None:
        silent = working_days_between(last_log + timedelta(days=1), today, hol)
        stale = silent > cfg.stale_workdays

    health = combine(ratio, stage_slip, ship_slip, stale)

    recovery = 0
    if required is not None:
        recovery = max(0, math.ceil(required - actual))

    return OrderHealthResult(
        order_id=inp.order_id, health=health, active_stage=active.key, qty=inp.qty,
        done=active.done, remaining=remaining, required_per_day=required,
        actual_per_day=actual, working_days_left=max(days_left, 0), overdue=overdue,
        stage_deadline=active.deadline, projected_finish=finish, stage_slip_days=stage_slip,
        projected_ship_date=ship, ship_slip_days=ship_slip, projected_at_deadline=at_deadline,
        ratio=ratio, low_confidence=low_confidence, stale=stale, last_log_date=last_log,
        lead_days=lead_days, recovery_per_day=recovery,
    )
