"""Idempotent daily-log ingestion (F-1, BR-02, BR-04, BR-09, BR-10, FR-05, FR-07, FR-09)."""
from __future__ import annotations

from datetime import timedelta

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from backend.app.clock import get_today
from backend.app.config import get_config
from backend.app.errors import AppError
from backend.app.models import DailyLog, Milestone
from backend.app.schemas.common import LogInput
from backend.app.services import warnings as warn
from backend.app.services.health import health_for
from backend.app.services.notes import attach_note
from backend.app.services.scope import SupervisorScope


def _fields(field: str, message: str) -> AppError:
    return AppError(422, message, {field: message})


def stage_done(session: Session, order_id: str, stage: str) -> int:
    return int(session.scalar(select(func.coalesce(func.sum(DailyLog.qty), 0)).where(
        DailyLog.order_id == order_id, DailyLog.stage_key == stage, DailyLog.superseded_by_id.is_(None))) or 0)


def submit_log(scope: SupervisorScope, body: LogInput) -> tuple[bool, str]:
    """Returns (created, log_id). created=False means the same id was already stored (HTTP 200)."""
    s, cfg = scope.session, get_config()
    order = scope.get_order(body.order_id)  # 403 for another unit's order (FR-06)
    if body.stage_key not in scope.assigned_stages(order.id):
        raise AppError(403, "This stage is not assigned to your unit.")

    existing = s.get(DailyLog, body.id)
    if existing is not None:
        if existing.order_id != order.id or existing.entered_by_id != scope.principal.user_id:
            raise AppError(409, "This id was used for a different entry.")
        return False, existing.id  # idempotent replay: no new row, no side effects

    today = get_today()
    if body.log_date > today:
        raise _fields("logDate", "The date cannot be in the future.")
    if body.log_date < today - timedelta(days=cfg.backdate_days):
        raise _fields("logDate", f"You can only enter the last {cfg.backdate_days} days.")

    old = s.scalar(select(DailyLog).where(
        DailyLog.order_id == order.id, DailyLog.stage_key == body.stage_key,
        DailyLog.log_date == body.log_date, DailyLog.superseded_by_id.is_(None)))
    cumulative = stage_done(s, order.id, body.stage_key) - (old.qty if old else 0) + body.qty
    if cumulative > cfg.qty_cap * order.qty:  # BR-09: server-side 105% guard
        raise _fields("qty", "That would be more than the order quantity allows.")

    prev = health_for(s, [order], today)[order.id]

    try:
        with s.begin_nested():
            if old is not None:
                # The FK needs the target to exist, so point the old row at itself first: it stops being
                # "effective" (frees the partial unique index) and is repointed once the new row exists.
                old.superseded_by_id = old.id
                s.flush()
            res = s.execute(pg_insert(DailyLog).values(
                id=body.id, order_id=order.id, stage_key=body.stage_key, log_date=body.log_date, qty=body.qty,
                entered_by_id=scope.principal.user_id, client_created_at=body.client_created_at)
                .on_conflict_do_nothing(index_elements=["id"]))
            if res.rowcount == 0:  # lost a race with an identical retry
                raise _Replay
            if old is not None:
                s.execute(update(DailyLog).where(DailyLog.id == old.id).values(superseded_by_id=body.id))
    except _Replay:
        return False, body.id

    _sync_stage_milestone(s, order.id, body.stage_key, order.qty, body.log_date)
    s.flush()
    s.expire_all()
    new = health_for(s, [order], today)[order.id]
    warn.upsert_draft(s, order.id, prev, new)  # BR-04
    s.commit()  # the numbers are durable before any AI call

    if body.note_text and body.note_text.strip():
        log_row = s.get(DailyLog, body.id)
        attach_note(s, log_row, body.note_text.strip(), scope.principal.user_id)
        s.commit()
    return True, body.id


class _Replay(Exception):
    pass


def _sync_stage_milestone(s: Session, order_id: str, stage: str, qty: int, log_date) -> None:
    """FR-05: a STAGE milestone completes automatically when logged quantity reaches the order quantity."""
    done = stage_done(s, order_id, stage)
    m = s.scalar(select(Milestone).where(Milestone.order_id == order_id, Milestone.stage_key == stage,
                                         Milestone.kind == "STAGE"))
    if m is None:
        return
    if done >= qty and m.actual_date is None:
        m.actual_date = log_date
    elif done < qty and m.actual_date is not None:  # a correction lowered the total
        m.actual_date = None
