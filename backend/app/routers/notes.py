from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from backend.app.config import get_config
from backend.app.errors import AppError
from backend.app.models import IssueNote
from backend.app.schemas.common import NoteView
from backend.app.schemas.misc import CategoryIn
from backend.app.services.scope import MerchScope, merch_scope
from backend.app.services.warnings import note_view

router = APIRouter(tags=["notes"])


@router.get("/notes", response_model=list[NoteView])
def list_notes(order_id: str = Query(..., alias="orderId"), scope: MerchScope = Depends(merch_scope)) -> list[NoteView]:
    order = scope.get_order(order_id)
    rows = scope.session.scalars(select(IssueNote).where(IssueNote.order_id == order.id)
                                 .order_by(IssueNote.created_at.desc()))
    return [note_view(n, get_config().ai_confidence_min) for n in rows]


@router.patch("/notes/{note_id}", response_model=NoteView)
def set_category(note_id: str, body: CategoryIn, scope: MerchScope = Depends(merch_scope)) -> NoteView:
    n = scope.session.get(IssueNote, note_id)
    if n is None:
        raise AppError(404, "Note not found.")
    scope.get_order(n.order_id)
    n.category, n.source = body.category, "HUMAN"  # FR-15: stored with who and when
    n.reviewed_by_id, n.reviewed_at = scope.principal.user_id, datetime.now(UTC)
    scope.session.commit()
    return note_view(n, get_config().ai_confidence_min)
