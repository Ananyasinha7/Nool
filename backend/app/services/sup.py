"""Supervisor home cards (S-6, BR-08): numbers only, no status colours."""
from __future__ import annotations

from collections import defaultdict
import math

from sqlalchemy import select

from backend.app.clock import get_today
from backend.app.models import DailyLog, Order, StageAssignment
from backend.app.projection.workdays import working_days_between
from backend.app.schemas.common import SupOrderCard
from backend.app.services.health import build_inputs, load_holidays
from backend.app.services.scope import SupervisorScope


def cards(scope: SupervisorScope) -> list[SupOrderCard]:
    s, today = scope.session, get_today()
    orders = list(s.scalars(scope.order_query().order_by(Order.ex_factory)))
    if not orders:
        return []
    ids = [o.id for o in orders]
    inputs = build_inputs(s, orders)
    holidays = load_holidays(s)

    # Batch fetch assigned stages in 1 query instead of N sequential round-trips
    assigned_q = select(StageAssignment.order_id, StageAssignment.stage_key).where(
        StageAssignment.order_id.in_(ids),
        StageAssignment.unit_id == scope.unit_id,
    )
    assigned_by_order: dict[str, set[str]] = defaultdict(set)
    for oid, skey in s.execute(assigned_q):
        assigned_by_order[oid].add(skey)

    out: list[SupOrderCard] = []
    for o in orders:
        mine = assigned_by_order.get(o.id, set())
        for st in inputs[o.id].stages:
            if st.key not in mine or st.done >= o.qty:
                continue  # one card per assigned, incomplete stage (Doc3 section 17)
            days = max(1, working_days_between(today, st.deadline, holidays))
            today_qty = next((q for d, q in st.logs if d == today), None)
            out.append(SupOrderCard(order_id=o.id, po_no=o.po_no, style=f"{o.style}, {o.colour}",
                                    stage_key=st.key, qty=o.qty, done=st.done,
                                    needed_today=math.ceil((o.qty - st.done) / days), today_qty=today_qty))
    return out


__all__ = ["cards", "select", "DailyLog"]
