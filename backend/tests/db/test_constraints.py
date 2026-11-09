"""DB-level guarantees (FR-19, BR-02, BR-04). Skipped without TEST_DATABASE_URL."""
from datetime import UTC, date, datetime

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError, IntegrityError

from backend.app.models import DailyLog, ExFactoryChange, Order, User, Warning


def _order_and_user(db):
    return db.scalar(select(Order).where(Order.po_no == "B-PO-88213")), db.scalar(select(User))


def test_ex_factory_history_cannot_be_updated(db):
    with pytest.raises(DBAPIError, match="append-only"):
        with db.begin_nested():
            db.execute(text("UPDATE ex_factory_changes SET reason_code='X'"))


def test_ex_factory_history_cannot_be_deleted(db):
    with pytest.raises(DBAPIError, match="append-only"):
        with db.begin_nested():
            db.execute(text("DELETE FROM ex_factory_changes"))


def test_audit_log_is_append_only(db):
    db.execute(text("INSERT INTO audit_log (id, action, entity, entity_id, meta) VALUES ('a','x','y','z','{}')"))
    with pytest.raises(DBAPIError, match="append-only"):
        with db.begin_nested():
            db.execute(text("UPDATE audit_log SET action='q'"))


def test_history_can_still_be_appended(db):
    o, u = _order_and_user(db)
    db.add(ExFactoryChange(order_id=o.id, from_date=date(2026, 11, 20), to_date=date(2026, 11, 21),
                           reason_code="OTHER", changed_by_id=u.id))
    db.flush()


def test_only_one_effective_log_per_day(db):
    o = db.scalar(select(Order).where(Order.po_no == "B-PO-88213"))
    existing = db.scalar(select(DailyLog).where(DailyLog.order_id == o.id, DailyLog.superseded_by_id.is_(None),
                                                DailyLog.stage_key == "STITCHING"))
    dup = DailyLog(id="11111111-1111-1111-1111-111111111111", order_id=o.id, stage_key="STITCHING",
                   log_date=existing.log_date, qty=1, entered_by_id=existing.entered_by_id,
                   client_created_at=datetime.now(UTC))
    with pytest.raises(IntegrityError):
        with db.begin_nested():
            db.add(dup)
            db.flush()


def test_only_one_open_draft_warning_per_order(db):
    w = db.scalar(select(Warning).where(Warning.status == "DRAFT"))
    with pytest.raises(IntegrityError):
        with db.begin_nested():
            db.add(Warning(order_id=w.order_id, status="DRAFT", health="RED", snapshot={}))
            db.flush()


def test_negative_quantity_rejected(db):
    o = db.scalar(select(Order).where(Order.po_no == "B-PO-88213"))
    u = db.scalar(select(User))
    with pytest.raises(IntegrityError):
        with db.begin_nested():
            db.add(DailyLog(id="22222222-2222-2222-2222-222222222222", order_id=o.id, stage_key="CUTTING",
                            log_date=date(2026, 1, 5), qty=-1, entered_by_id=u.id,
                            client_created_at=datetime.now(UTC)))
            db.flush()
