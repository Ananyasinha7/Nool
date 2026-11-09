"""Warning lifecycle helpers (F-2, BR-04, BR-05, D-17)."""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import IssueNote, Order, Warning
from backend.app.schemas.common import BuyerPreview, NoteView, OrderHealth, WarningView

CATEGORY_LABEL = {
    "MACHINE_BREAKDOWN": "Machine breakdown", "POWER_CUT": "Power cut", "ABSENTEEISM": "Staff absence",
    "MATERIAL_SHORTAGE": "Material shortage", "QUALITY_REWORK": "Quality rework",
    "SUBCONTRACTOR_DELAY": "Subcontractor delay", "APPROVAL_PENDING": "Approval pending",
    "OTHER": "Production issue", "NEEDS_REVIEW": "Production issue",
}
_RANK = {"GREEN": 0, "GREY": 0, "AMBER": 1, "RED": 2}


def buyer_text(category: str, ship_slip_days: int) -> str:
    """Exactly what a buyer sees: category label plus date impact, never the raw note (D-17)."""
    label = CATEGORY_LABEL.get(category, "Production issue")
    if ship_slip_days > 0:
        unit = "day" if ship_slip_days == 1 else "days"
        return f"Delay notice · {label} · ship date may move by about {ship_slip_days} {unit}"
    return f"Delay notice · {label} · we are monitoring the ship date"


def worsened(prev: OrderHealth | None, new: OrderHealth) -> bool:
    """BR-04: status becomes amber or red, or the projected slip grows by at least one working day."""
    if new.health not in ("AMBER", "RED"):
        return False
    if prev is None:
        return True
    return prev.health != new.health and _RANK[new.health] > _RANK[prev.health] or (
        new.stage_slip_days - prev.stage_slip_days >= 1)


def open_draft(session: Session, order_id: str) -> Warning | None:
    return session.scalar(select(Warning).where(Warning.order_id == order_id, Warning.status == "DRAFT"))


def upsert_draft(session: Session, order_id: str, prev: OrderHealth | None, new: OrderHealth,
                 note_id: str | None = None) -> Warning | None:
    """Create or update the single open draft. A non-worsening update only refreshes an existing draft's
    maths so the merchandiser never reviews stale numbers."""
    draft = open_draft(session, order_id)
    snap = new.model_dump(mode="json", by_alias=True)
    if draft is None:
        if not worsened(prev, new):
            return None
        draft = Warning(order_id=order_id, status="DRAFT", health=new.health, snapshot=snap, note_id=note_id)
        session.add(draft)
    else:
        draft.health, draft.snapshot = new.health, snap
        draft.updated_at = datetime.now(UTC)
        if note_id:
            draft.note_id = note_id
    session.flush()
    return draft


def note_view(n: IssueNote, confidence_min: float) -> NoteView:
    needs = n.category == "NEEDS_REVIEW" or n.source == "RULE" or (
        n.source == "AI" and n.confidence is not None and n.confidence < confidence_min)
    return NoteView(id=n.id, original_text=n.original_text, lang="ta" if n.lang == "ta" else "en",
                    translation_en=n.translation_en, category=n.category, confidence=n.confidence,
                    source=n.source, needs_review=needs)


def warning_view(session: Session, w: Warning, confidence_min: float) -> WarningView:
    return warning_views(session, [w], confidence_min)[0]


def warning_views(session: Session, warnings: list[Warning], confidence_min: float) -> list[WarningView]:
    if not warnings:
        return []
    order_ids = {w.order_id for w in warnings}
    note_ids = {w.note_id for w in warnings if w.note_id}

    if order_ids and note_ids:
        from concurrent.futures import ThreadPoolExecutor
        from backend.app.db import get_sessionmaker

        sm = get_sessionmaker()

        def fetch_orders():
            with sm() as s:
                return {o.id: o for o in s.scalars(select(Order).where(Order.id.in_(order_ids)))}

        def fetch_notes():
            with sm() as s:
                return {n.id: n for n in s.scalars(select(IssueNote).where(IssueNote.id.in_(note_ids)))}

        with ThreadPoolExecutor(max_workers=2) as pool:
            f_o = pool.submit(fetch_orders)
            f_n = pool.submit(fetch_notes)
            orders_map = f_o.result()
            notes_map = f_n.result()
    else:
        orders_map = {o.id: o for o in session.scalars(select(Order).where(Order.id.in_(order_ids)))} if order_ids else {}
        notes_map = {n.id: n for n in session.scalars(select(IssueNote).where(IssueNote.id.in_(note_ids)))} if note_ids else {}

    out: list[WarningView] = []
    for w in warnings:
        order = orders_map.get(w.order_id)
        note = notes_map.get(w.note_id) if w.note_id else None
        snapshot = OrderHealth.model_validate(w.snapshot)
        category = w.category_final or (note.category if note else "NEEDS_REVIEW")
        out.append(WarningView(
            id=w.id, order_id=w.order_id, po_no=order.po_no if order else "", health=w.health, snapshot=snapshot,
            note=note_view(note, confidence_min) if note else None, status=w.status,
            buyer_preview=BuyerPreview(category=category, ship_slip_days=snapshot.ship_slip_days,
                                       text=buyer_text(category, snapshot.ship_slip_days))))
    return out
