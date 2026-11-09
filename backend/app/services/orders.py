"""Order helpers shared by the API and the seed (F-3)."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import (
    Milestone,
    Order,
    OrderLine,
    StageAssignment,
    TnaItem,
    Unit,
    Warning,
)
from backend.app.schemas.common import OrderHealth
from backend.app.schemas.orders import (
    AssignmentOut,
    MilestoneOut,
    OrderDetail,
    OrderLineOut,
)

WASH_OFFSET_DAYS = 10  # Doc3 5.2 "add {WASHING, offsetDays 10}" when the order has a wash


@dataclass(frozen=True)
class MilestonePlan:
    name: str
    kind: str
    stage_key: str | None
    planned_date: date
    sort_order: int


def milestone_plan(items: list[TnaItem], ex_factory: date, has_print: bool, has_wash: bool) -> list[MilestonePlan]:
    """Deadline = ex-factory minus offsetDays (calendar days). printOnly items are skipped
    without print; washing is added when the order has a wash."""
    rows: list[tuple[str, str, str | None, int]] = []
    for it in items:
        if it.print_only and not has_print:
            continue
        rows.append((it.name, it.kind, it.stage_key, it.offset_days))
    if has_wash:
        rows.append(("Washing complete", "STAGE", "WASHING", WASH_OFFSET_DAYS))
    # Sort by planned date (largest offset first) so the timeline reads top to bottom.
    rows.sort(key=lambda r: -r[3])
    return [MilestonePlan(n, k, s, ex_factory - timedelta(days=off), i) for i, (n, k, s, off) in enumerate(rows)]


def iso_week(d: date) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def assignments_map(session: Session, order_ids: list[str]) -> dict[str, dict[str, tuple[str, str]]]:
    """order -> stage -> (unit id, unit name), in one query."""
    out: dict[str, dict[str, tuple[str, str]]] = defaultdict(dict)
    q = select(StageAssignment.order_id, StageAssignment.stage_key, Unit.id, Unit.name).join(
        Unit, Unit.id == StageAssignment.unit_id).where(StageAssignment.order_id.in_(order_ids))
    for oid, stage, uid, uname in session.execute(q):
        out[oid][stage] = (uid, uname)
    return out


def open_warning_ids(session: Session, order_ids: list[str]) -> set[str]:
    return set(session.scalars(select(Warning.order_id).where(Warning.order_id.in_(order_ids),
                                                            Warning.status == "DRAFT")))


def detail(session: Session, order: Order, health: OrderHealth) -> OrderDetail:
    miles = session.scalars(select(Milestone).where(Milestone.order_id == order.id)
                            .order_by(Milestone.sort_order)).all()
    lines = session.scalars(select(OrderLine).where(OrderLine.order_id == order.id)).all()
    amap = assignments_map(session, [order.id]).get(order.id, {})
    return OrderDetail(
        id=order.id, po_no=order.po_no, buyer_id=order.buyer_id, buyer_name=order.buyer.name,
        style=order.style, colour=order.colour, qty=order.qty, has_print=order.has_print,
        has_wash=order.has_wash, ex_factory=order.ex_factory, ex_factory_original=order.ex_factory_original,
        template_id=order.template_id,
        lines=[OrderLineOut(size=ln.size, qty=ln.qty) for ln in lines],
        milestones=[MilestoneOut(id=m.id, name=m.name, kind=m.kind, stage_key=m.stage_key,
                                 planned_date=m.planned_date, actual_date=m.actual_date,
                                 sort_order=m.sort_order) for m in miles],
        assignments=[AssignmentOut(stage_key=k, unit_id=u, unit_name=n) for k, (u, n) in amap.items()],
        health=health, open_warning=order.id in open_warning_ids(session, [order.id]))


def _field_error(field: str, message: str):
    from backend.app.errors import AppError

    return AppError(422, "Please check the highlighted fields.", {field: message})


def create_order(session: Session, body, actor_id: str) -> Order:
    """F-3: validate, insert order + lines + stage assignments, generate milestones from the template."""
    from backend.app.errors import AppError
    from backend.app.models import Buyer, TnaTemplate

    if session.scalar(select(Order.id).where(Order.po_no == body.po_no.strip())):
        raise AppError(409, "This PO already exists.", {"poNo": "This PO already exists."})
    total = sum(line.qty for line in body.lines)
    if body.qty is not None and body.qty != total:
        raise _field_error("qty", "Total must equal the sum of the size lines.")
    if session.get(Buyer, body.buyer_id) is None:
        raise _field_error("buyerId", "Choose a buyer.")
    tpl = session.get(TnaTemplate, body.template_id)
    if tpl is None:
        raise _field_error("templateId", "Choose a TNA template.")
    unit_ids = {u.id for u in session.scalars(select(Unit))}
    for fld, uid in (("unitId", body.unit_id), ("printUnitId", body.print_unit_id), ("washUnitId", body.wash_unit_id)):
        if uid is not None and uid not in unit_ids:
            raise _field_error(fld, "Choose a unit.")

    order = Order(po_no=body.po_no.strip(), buyer_id=body.buyer_id, style=body.style.strip(),
                  colour=body.colour.strip(), qty=total, has_print=body.has_print, has_wash=body.has_wash,
                  ex_factory=body.ex_factory, ex_factory_original=body.ex_factory, template_id=tpl.id,
                  created_by_id=actor_id)
    session.add(order)
    session.flush()
    for line in body.lines:
        session.add(OrderLine(order_id=order.id, size=line.size.strip(), qty=line.qty))

    flow = [k for k in ("CUTTING", "PRINTING", "STITCHING", "WASHING", "FINISHING", "PACKING")
            if (k != "PRINTING" or body.has_print) and (k != "WASHING" or body.has_wash)]
    for k in flow:
        uid = body.unit_id
        if k == "PRINTING" and body.print_unit_id:
            uid = body.print_unit_id
        if k == "WASHING" and body.wash_unit_id:
            uid = body.wash_unit_id
        session.add(StageAssignment(order_id=order.id, stage_key=k, unit_id=uid))

    overrides = body.milestone_dates or {}
    for p in milestone_plan(list(tpl.items), body.ex_factory, body.has_print, body.has_wash):
        session.add(Milestone(order_id=order.id, name=p.name, kind=p.kind, stage_key=p.stage_key,
                              planned_date=overrides.get(p.name, p.planned_date), sort_order=p.sort_order))
    session.flush()
    return order


def change_ex_factory(session: Session, order: Order, to_date: date, reason_code: str, reason_text: str | None,
                      actor_id: str) -> None:
    """F-4: one transaction: history row, new date, recomputed milestone dates, audit entry."""
    from backend.app.models import ExFactoryChange
    from backend.app.services.audit import audit

    if to_date == order.ex_factory:
        raise _field_error("toDate", "Choose a different date.")
    if reason_code == "OTHER" and not (reason_text or "").strip():
        raise _field_error("reasonText", "Please add a short reason.")
    old = order.ex_factory
    session.add(ExFactoryChange(order_id=order.id, from_date=old, to_date=to_date, reason_code=reason_code,
                                reason_text=(reason_text or None), changed_by_id=actor_id))
    order.ex_factory = to_date
    offsets = {it.name: it.offset_days
               for it in session.scalars(select(TnaItem).where(TnaItem.template_id == order.template_id))}
    offsets["Washing complete"] = WASH_OFFSET_DAYS
    delta = to_date - old
    for m in session.scalars(select(Milestone).where(Milestone.order_id == order.id)):
        # Template offsets keep the plan shape; unknown (custom) items just move with the date.
        m.planned_date = to_date - timedelta(days=offsets[m.name]) if m.name in offsets else m.planned_date + delta
    audit(session, actor_id, "EX_FACTORY_CHANGED", "order", order.id, fromDate=old, toDate=to_date,
          reason=reason_code)
    session.flush()
