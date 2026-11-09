"""Seed orders: the 3 client samples (exact done quantities) plus 10 synthetic orders."""
from __future__ import annotations

import math
import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import (
    DailyLog,
    ExFactoryChange,
    IssueNote,
    Milestone,
    Order,
    OrderLine,
    OutboxMessage,
    Photo,
    PhotoBlob,
    StageAssignment,
    TnaTemplate,
    Warning,
)
from backend.app.projection.workdays import working_days_between
from backend.app.services.health import FLOW, health_for
from backend.app.services.orders import milestone_plan
from backend.seed.history import HISTORY_START, active_stage_logs, completed_stage_logs, working_days
from backend.seed.notes import CONFIRMED_WARNING, DATE_CHANGES, DRAFT_WARNINGS, NOTES
from backend.seed.photos import make_swatch
from backend.seed.reference import HOLIDAYS

DEMO_TODAY = date(2026, 11, 3)  # A-13: seeded history is anchored to this date
NS = uuid.UUID("6f1d3c0e-0000-4000-8000-00000000a001")
SIZES_ADULT = [("S", 0.10), ("M", 0.25), ("L", 0.30), ("XL", 0.25), ("XXL", 0.10)]  # A-04
SIZES_KIDS = [("4-5Y", 0.25), ("6-7Y", 0.25), ("8-9Y", 0.25), ("10-11Y", 0.25)]

# po, buyer, style, colour, qty, ex-factory, active stage, done, target ratio, target status,
# has_print, unit for non-print stages, last-3 logs latest first (samples) or None
ORDERS = [
    ("B-PO-88213", "Company B", "Men's crew neck tee", "navy", 12000, "2026-11-20", "STITCHING", 6800, None,
     "AMBER", False, "Unit 1", [490, 480, 465]),
    ("B-PO-88240", "Company B", "Men's polo", "white", 8000, "2026-11-12", "FINISHING", 5200, None,
     "RED", False, "Unit 2", [290, 310, 305]),
    ("C-PO-0488", "Company C", "Kids printed tee", "yellow", 10000, "2026-11-28", "PRINTING", 3100, None,
     "GREEN", True, "Unit 3", [810, 790, 800]),
    ("B-PO-88301", "Company B", "Women's rib tank", "white", 9000, "2026-12-04", "STITCHING", 2000, 0.72,
     "RED", False, "Unit 1", None),
    ("B-PO-88317", "Company B", "Men's hoodie", "grey", 6000, "2026-12-10", "CUTTING", 2400, 0.88,
     "AMBER", False, "Unit 2", None),
    ("C-PO-0491", "Company C", "Kids hoodie", "blue", 7000, "2026-12-01", "PRINTING", 1500, 0.85,
     "AMBER", True, "Unit 3", None),
    ("C-PO-0502", "Company C", "Kids leggings", "pink", 5000, "2026-12-15", "CUTTING", 800, 1.10,
     "GREEN", False, "Unit 3", None),
    ("D-PO-7710", "Company D", "Women's tee", "sage", 11000, "2026-11-24", "STITCHING", 7400, 1.05,
     "GREEN", False, "Unit 2", None),
    ("D-PO-7722", "Company D", "Men's sweatshirt", "navy", 8500, "2026-12-18", "CUTTING", 600, 1.20,
     "GREEN", False, "Unit 2", None),
    ("D-PO-7735", "Company D", "Women's cardigan", "oat", 4000, "2026-11-30", "FINISHING", 3100, 1.08,
     "GREEN", False, "Unit 3", None),
    ("B-PO-88329", "Company B", "Kids polo", "red", 6500, "2026-12-08", "STITCHING", 1000, 1.02,
     "GREEN", False, "Unit 1", None),
    ("C-PO-0510", "Company C", "Men's tee", "olive", 9500, "2026-12-20", "CUTTING", 700, None,
     "GREY", False, "Unit 3", None),
    ("B-PO-88340", "Company B", "Women's polo", "black", 7500, "2026-12-22", "CUTTING", 340, 1.00,
     "GREEN", False, "Unit 1", None),
]
GREY_LAST_LOG = date(2026, 10, 28)
# B-PO-88340: Doc3 lists done=300, but 300 pieces total can never reach the 313/day needed (GREEN).
# Seeded as 340 (decision D-21, pending owner review).


def _stage_flow(has_print: bool) -> list[str]:
    return [s for s in FLOW if s not in ("WASHING",) and (s != "PRINTING" or has_print)]


def _lines(qty: int, kids: bool) -> list[tuple[str, int]]:
    split = SIZES_KIDS if kids else SIZES_ADULT
    out = [(sz, int(qty * share)) for sz, share in split]
    out[-1] = (out[-1][0], out[-1][1] + qty - sum(q for _, q in out))
    return out


def _uid(*parts: object) -> str:
    return str(uuid.uuid5(NS, "|".join(str(p) for p in parts)))


def seed_orders(s: Session, ids: dict[str, dict]) -> int:
    holidays = frozenset(d for d, _ in HOLIDAYS)
    tpl = s.get(TnaTemplate, ids["template"]["Standard"])
    priya = ids["users"]["priya.merch"]
    sup_of_unit = {"Unit 1": "murugan.u1", "Unit 2": "selvi.u2", "Unit 3": "anbu.u3", "Print House": "kumar.print"}
    created: dict[str, Order] = {}
    last_log_id: dict[str, str] = {}
    stage_logs_by_order: dict[str, dict[str, list[DailyLog]]] = {}

    for (po, buyer, style, colour, qty, ex, active, done, ratio, _status, has_print, unit,
         last3) in ORDERS:
        if s.scalar(select(Order).where(Order.po_no == po)):
            continue
        ex_d = date.fromisoformat(ex)
        original = date(2026, 11, 11) if po == "B-PO-88213" else ex_d
        order = Order(po_no=po, buyer_id=ids["buyers"][buyer], style=style, colour=colour, qty=qty,
                      has_print=has_print, has_wash=False, ex_factory=ex_d, ex_factory_original=original,
                      template_id=tpl.id, created_by_id=priya)
        s.add(order)
        s.flush()
        created[po] = order
        for size, q in _lines(qty, "Kids" in style):
            s.add(OrderLine(order_id=order.id, size=size, qty=q))

        flow = _stage_flow(has_print)
        units = {k: ("Print House" if (k == "PRINTING") else unit) for k in flow}
        for k in flow:
            s.add(StageAssignment(order_id=order.id, stage_key=k, unit_id=ids["units"][units[k]]))

        plans = milestone_plan(list(tpl.items), ex_d, has_print, False)
        deadlines = {p.stage_key: p.planned_date for p in plans if p.stage_key}

        # --- logs ---
        required = None
        if last3 is None:
            remaining = qty - done
            dl = max(1, working_days_between(DEMO_TODAY, deadlines[active], holidays))
            required = remaining / dl
            r = math.ceil(required * (ratio or 1.0))
            last3 = [r, r, r]
        end = GREY_LAST_LOG if po == "C-PO-0510" else DEMO_TODAY - timedelta(days=1)
        days = working_days(HISTORY_START, end, holidays)
        per_stage: dict[str, list[DailyLog]] = {}
        idx = flow.index(active)
        window_end = HISTORY_START
        for k in reversed(flow[:idx]):
            rows = completed_stage_logs(qty, window_end, holidays)
            window_end = rows[0][0]
            _add_logs(s, order, k, rows, sup_of_unit[units[k]], ids, per_stage)
        if po == "C-PO-0510":
            # One catch-up batch on the last day logged: stale (GREY) but with a healthy rate, so
            # GREY cannot be masking a hidden problem.
            rows = [(GREY_LAST_LOG, done)]
        else:
            rows = active_stage_logs(days, done, last3)
        _add_logs(s, order, active, rows, sup_of_unit[units[active]], ids, per_stage)
        stage_logs_by_order[po] = per_stage
        last_log_id[po] = per_stage[active][-1].id

        # --- milestones ---
        for p in plans:
            actual = None
            if p.kind == "STAGE" and p.stage_key in per_stage and flow.index(p.stage_key) < idx:
                actual = max(lg.log_date for lg in per_stage[p.stage_key])
            elif p.kind == "MANUAL" and p.planned_date <= DEMO_TODAY:
                actual = p.planned_date
            s.add(Milestone(order_id=order.id, name=p.name, kind=p.kind, stage_key=p.stage_key,
                            planned_date=p.planned_date, actual_date=actual, sort_order=p.sort_order))
    s.flush()

    now = datetime(2026, 11, 3, 9, 0, tzinfo=UTC)
    # --- date changes ---
    for po, changes in DATE_CHANGES.items():
        if po in created:
            for frm, to, code, text, days_ago in changes:
                s.add(ExFactoryChange(order_id=created[po].id, from_date=date.fromisoformat(frm),
                                      to_date=date.fromisoformat(to), reason_code=code, reason_text=text,
                                      changed_by_id=priya, changed_at=now - timedelta(days=days_ago)))

    # --- notes ---
    note_rows: list[IssueNote] = []
    for po, text, lang, translation, cat, conf in NOTES:
        if po not in created:
            note_rows.append(None)  # type: ignore[arg-type]
            continue
        note = IssueNote(log_id=last_log_id[po], order_id=created[po].id, original_text=text, lang=lang,
                         translation_en=translation, category=cat, confidence=conf, source="AI")
        s.add(note)
        note_rows.append(note)
    s.flush()

    # --- warnings (snapshot = frozen maths at seed time) ---
    health = health_for(s, created.values(), DEMO_TODAY)

    def warn(po: str, note_idx: int, status: str) -> Warning | None:
        if po not in created:
            return None
        h = health[created[po].id]
        w = Warning(order_id=created[po].id, status=status, health=h.health,
                    snapshot=h.model_dump(mode="json", by_alias=True), note_id=note_rows[note_idx].id,
                    category_final=NOTES[note_idx][4] if status == "CONFIRMED" else None)
        if status == "CONFIRMED":
            w.confirmed_by_id, w.confirmed_at = priya, now - timedelta(days=1)
        s.add(w)
        return w

    for po, i in DRAFT_WARNINGS.items():
        warn(po, i, "DRAFT")
    confirmed = warn(CONFIRMED_WARNING[0], CONFIRMED_WARNING[1], "CONFIRMED")
    s.flush()

    # --- outbox (mock messages) ---
    if confirmed is not None:
        s.add(OutboxMessage(buyer_id=ids["buyers"]["Company B"], warning_id=confirmed.id,
                            subject="Delay notice: B-PO-88213",
                            body="Machine breakdown at the stitching unit. We are monitoring the ship date."))
        s.add(OutboxMessage(buyer_id=ids["buyers"]["Company C"],
                            subject="Weekly status (demo)", body="Your weekly order status is attached."))

    # --- photos: 8 placeholders, 3 shared ---
    colours = [(46, 125, 91), (201, 138, 27), (194, 65, 45), (74, 82, 96)]
    plan = [("B-PO-88213", True), ("B-PO-88213", True), ("B-PO-88213", False), ("B-PO-88240", False),
            ("B-PO-88240", False), ("C-PO-0488", True), ("C-PO-0488", False), ("B-PO-88301", False)]
    for i, (po, shared) in enumerate(plan):
        if po not in created:
            continue
        pid = _uid("photo", po, i)
        if s.get(Photo, pid):
            continue
        blob = make_swatch(f"{po} photo {i + 1}", colours[i % 4])
        s.add(Photo(id=pid, log_id=last_log_id[po], mime="image/jpeg", size_bytes=len(blob),
                    share_with_buyer=shared))
        s.flush()
        s.add(PhotoBlob(photo_id=pid, bytes=blob))
    s.flush()
    return len(created)


def _add_logs(s: Session, order: Order, stage: str, rows: list[tuple[date, int]], sup: str, ids: dict,
              out: dict[str, list[DailyLog]]) -> None:
    for d, q in rows:
        log = DailyLog(id=_uid("log", order.po_no, stage, d), order_id=order.id, stage_key=stage, log_date=d,
                       qty=q, entered_by_id=ids["users"][sup],
                       client_created_at=datetime.combine(d, datetime.min.time(), tzinfo=UTC))
        s.add(log)
        out.setdefault(stage, []).append(log)
    s.flush()
