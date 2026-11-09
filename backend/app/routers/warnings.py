from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from backend.app.config import get_config
from backend.app.errors import AppError
from backend.app.models import IssueNote, Order, OutboxMessage, Warning
from backend.app.schemas.common import WarningView
from backend.app.schemas.misc import CategoryIn
from backend.app.services.audit import audit
from backend.app.services.scope import MerchScope, merch_scope
from backend.app.services.warnings import buyer_text, warning_view, warning_views

router = APIRouter(tags=["warnings"])


def _get_draft(scope: MerchScope, warning_id: str) -> Warning:
    w = scope.session.get(Warning, warning_id)
    if w is None:
        raise AppError(404, "Warning not found.")
    scope.get_order(w.order_id)
    if w.status != "DRAFT":
        raise AppError(409, "This warning was already handled.")
    return w


@router.get("/warnings", response_model=list[WarningView])
def list_warnings(status: Literal["DRAFT", "CONFIRMED", "DISMISSED"] | None = Query(None),
                  scope: MerchScope = Depends(merch_scope)) -> list[WarningView]:
    q = select(Warning).order_by(Warning.updated_at.desc())
    q = q.where(Warning.status == (status or "DRAFT"))
    cm = get_config().ai_confidence_min
    warnings_list = list(scope.session.scalars(q))
    return warning_views(scope.session, warnings_list, cm)


@router.post("/warnings/{warning_id}/confirm", response_model=WarningView)
def confirm(warning_id: str, body: CategoryIn, scope: MerchScope = Depends(merch_scope)) -> WarningView:
    s, cm = scope.session, get_config().ai_confidence_min
    w = _get_draft(scope, warning_id)
    now = datetime.now(UTC)
    note = s.get(IssueNote, w.note_id) if w.note_id else None
    if note is not None and (note.category != body.category or note.source != "AI"):
        note.category, note.source = body.category, "HUMAN"  # a person decided (FR-15)
        note.reviewed_by_id, note.reviewed_at = scope.principal.user_id, now
    w.status, w.category_final = "CONFIRMED", body.category
    w.confirmed_by_id, w.confirmed_at = scope.principal.user_id, now  # snapshot stays frozen
    order = s.get(Order, w.order_id)
    ship_slip = int(w.snapshot.get("shipSlipDays", 0))
    s.add(OutboxMessage(buyer_id=order.buyer_id, warning_id=w.id, subject=f"Delay notice: {order.po_no}",
                        body=buyer_text(body.category, ship_slip)))  # mocked: nothing leaves the system
    audit(s, scope.principal.user_id, "WARNING_CONFIRMED", "warning", w.id, category=body.category)
    s.commit()
    return warning_view(s, w, cm)


@router.post("/warnings/{warning_id}/dismiss", response_model=WarningView)
def dismiss(warning_id: str, scope: MerchScope = Depends(merch_scope)) -> WarningView:
    w = _get_draft(scope, warning_id)
    w.status = "DISMISSED"
    audit(scope.session, scope.principal.user_id, "WARNING_DISMISSED", "warning", w.id)
    scope.session.commit()
    return warning_view(scope.session, w, get_config().ai_confidence_min)
