"""Loads database rows into HealthInput and calls the pure projection.

Batch-friendly: the board computes health for many orders with a fixed number
of queries (NFR-3), never one query per order.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

import time
from backend.app.models import DailyLog, Holiday, Milestone, Order
from backend.app.projection.project import compute_health
from backend.app.projection.types import HealthInput, StageInput
from backend.app.schemas.common import OrderHealth

FLOW = ("CUTTING", "PRINTING", "STITCHING", "WASHING", "FINISHING", "PACKING")  # A-02

_cached_holidays: tuple[float, frozenset[date]] | None = None


def load_holidays(session: Session) -> frozenset[date]:
    global _cached_holidays
    now = time.time()
    if _cached_holidays is None or now - _cached_holidays[0] > 300.0:
        h = frozenset(session.scalars(select(Holiday.date)))
        _cached_holidays = (now, h)
    return _cached_holidays[1]


def build_inputs(
    session: Session,
    orders: Iterable[Order],
    miles_data: dict[str, list[tuple[str | None, str, date]]] | None = None,
    logs_data: dict[tuple[str, str], list[tuple[date, int]]] | None = None,
) -> dict[str, HealthInput]:
    orders = list(orders)
    if not orders:
        return {}
    ids = [o.id for o in orders]
    holidays = load_holidays(session)

    if miles_data is None:
        miles: dict[str, list[tuple[str | None, str, date]]] = defaultdict(list)
        q_m = select(Milestone.order_id, Milestone.stage_key, Milestone.name, Milestone.planned_date).where(
            Milestone.order_id.in_(ids)
        )
        for oid, skey, name, pdate in session.execute(q_m):
            miles[oid].append((skey, name, pdate))
    else:
        miles = miles_data

    if logs_data is None:
        logs: dict[tuple[str, str], list[tuple[date, int]]] = defaultdict(list)
        q = select(DailyLog.order_id, DailyLog.stage_key, DailyLog.log_date, DailyLog.qty).where(
            DailyLog.order_id.in_(ids), DailyLog.superseded_by_id.is_(None)
        )
        for oid, stage, d, qty in session.execute(q):
            logs[(oid, stage)].append((d, qty))
    else:
        logs = logs_data

    out: dict[str, HealthInput] = {}
    for o in orders:
        deadlines = {skey: pdate for skey, _, pdate in miles[o.id] if skey}
        fabric = next(
            (pdate for _, name, pdate in miles[o.id] if name == "Fabric in-house"),
            o.ex_factory - timedelta(days=32),
        )
        stages: list[StageInput] = []
        prev_deadline: date | None = None
        for key in FLOW:
            if key not in deadlines:
                continue
            stage_logs = tuple(logs.get((o.id, key), ()))
            start = fabric if prev_deadline is None else prev_deadline + timedelta(days=1)
            stages.append(
                StageInput(
                    key,
                    deadlines[key],
                    start,
                    sum(q for _, q in stage_logs),
                    stage_logs,
                )
            )
            prev_deadline = deadlines[key]
        out[o.id] = HealthInput(o.id, o.qty, o.ex_factory, tuple(stages), holidays)
    return out


def health_for(
    session: Session,
    orders: Iterable[Order],
    today: date,
    inputs: dict[str, HealthInput] | None = None,
) -> dict[str, OrderHealth]:
    orders = list(orders)
    if inputs is None:
        inputs = build_inputs(session, orders)
    return {
        oid: OrderHealth.model_validate(_as_dict(compute_health(inp, today)))
        for oid, inp in inputs.items()
    }


def _as_dict(result: object) -> dict:
    from dataclasses import asdict

    return asdict(result)  # type: ignore[call-overload]
