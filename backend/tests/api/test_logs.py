import uuid
from datetime import date as _date

from sqlalchemy import func, select

from backend.app.models import DailyLog, IssueNote, Milestone, Order, Warning


def _oid(db, po):
    return db.scalar(select(Order.id).where(Order.po_no == po))


def _body(db, po="B-PO-88213", stage="STITCHING", qty=480, date="2026-11-03", **over):
    b = {"id": str(uuid.uuid4()), "orderId": _oid(db, po), "stageKey": stage, "logDate": date, "qty": qty,
         "clientCreatedAt": "2026-11-03T06:00:00Z"}
    b.update(over)
    return b


def _effective(db, po, stage, date):
    return db.scalars(select(DailyLog).where(DailyLog.order_id == _oid(db, po), DailyLog.stage_key == stage,
                                             DailyLog.log_date == _date.fromisoformat(date),
                                             DailyLog.superseded_by_id.is_(None))).all()


def test_first_post_201_then_same_id_200_no_new_row(as_murugan, db):
    b = _body(db)
    first = as_murugan.post("/api/logs", json=b)
    second = as_murugan.post("/api/logs", json=b)
    assert first.status_code == 201 and second.status_code == 200
    assert first.json() == second.json() == {"id": b["id"], "effective": True}
    assert db.scalar(select(func.count()).select_from(DailyLog).where(DailyLog.id == b["id"])) == 1


def test_same_day_correction_supersedes(as_murugan, db):
    a, b = _body(db, qty=100), _body(db, qty=250)
    assert as_murugan.post("/api/logs", json=a).status_code == 201
    assert as_murugan.post("/api/logs", json=b).status_code == 201
    eff = _effective(db, "B-PO-88213", "STITCHING", "2026-11-03")
    assert [e.qty for e in eff] == [250]  # totals count only the latest (BR-02)
    old = db.get(DailyLog, a["id"])
    assert old.superseded_by_id == b["id"]


def test_other_units_order_is_403(as_murugan, db):
    assert as_murugan.post("/api/logs", json=_body(db, po="B-PO-88240", stage="FINISHING")).status_code == 403


def test_unassigned_stage_is_403(as_murugan, db):
    assert as_murugan.post("/api/logs", json=_body(db, stage="PRINTING")).status_code == 403


def test_future_and_too_old_dates_rejected(as_murugan, db):
    assert as_murugan.post("/api/logs", json=_body(db, date="2026-11-04")).status_code == 422
    r = as_murugan.post("/api/logs", json=_body(db, date="2026-10-20"))
    assert r.status_code == 422 and "logDate" in r.json()["error"]["fields"]


def test_backdate_within_three_days_ok(as_murugan, db):
    assert as_murugan.post("/api/logs", json=_body(db, date="2026-10-31", qty=5)).status_code == 201


def test_over_105_percent_rejected(as_murugan, db):
    r = as_murugan.post("/api/logs", json=_body(db, po="B-PO-88340", stage="CUTTING", qty=8000))
    assert r.status_code == 422 and "qty" in r.json()["error"]["fields"]


def test_negative_quantity_rejected_by_schema(as_murugan, db):
    assert as_murugan.post("/api/logs", json=_body(db, qty=-1)).status_code == 422


def test_bad_uuid_rejected(as_murugan, db):
    assert as_murugan.post("/api/logs", json=_body(db, id="not-a-uuid")).status_code == 422


def test_merchandiser_cannot_post_logs(as_priya, db):
    assert as_priya.post("/api/logs", json=_body(db)).status_code == 403


def test_worsening_creates_one_draft_warning(as_murugan, db):
    assert db.scalar(select(Warning).where(Warning.order_id == _oid(db, "B-PO-88329"))) is None
    as_murugan.post("/api/logs", json=_body(db, po="B-PO-88329", qty=1))
    drafts = db.scalars(select(Warning).where(Warning.order_id == _oid(db, "B-PO-88329"),
                                              Warning.status == "DRAFT")).all()
    assert len(drafts) == 1 and drafts[0].health in ("AMBER", "RED")
    assert drafts[0].snapshot["workingDaysLeft"] >= 0  # the maths is frozen into the warning
    as_murugan.post("/api/logs", json=_body(db, po="B-PO-88329", qty=2, date="2026-11-02"))
    assert len(db.scalars(select(Warning).where(Warning.order_id == _oid(db, "B-PO-88329"),
                                                Warning.status == "DRAFT")).all()) == 1  # still one open draft


def test_healthy_log_creates_no_warning(as_murugan, db):
    as_murugan.post("/api/logs", json=_body(db, po="B-PO-88329", qty=400))
    assert db.scalar(select(Warning).where(Warning.order_id == _oid(db, "B-PO-88329"))) is None


def test_note_is_classified_after_commit(as_murugan, db):
    b = _body(db, po="B-PO-88329", qty=400, noteText="நீல நிற துணி வரவில்லை")
    assert as_murugan.post("/api/logs", json=b).status_code == 201
    note = db.scalar(select(IssueNote).where(IssueNote.log_id == b["id"]))
    assert note.category == "MATERIAL_SHORTAGE" and note.lang == "ta" and note.translation_en


def test_note_failure_never_loses_the_numbers(as_murugan, db, monkeypatch):
    import backend.app.services.notes as notes

    def boom(*a, **k):
        raise RuntimeError("ai exploded")

    monkeypatch.setattr(notes, "classify", boom)
    b = _body(db, po="B-PO-88329", qty=300, noteText="anything")
    assert as_murugan.post("/api/logs", json=b).status_code == 201
    assert db.get(DailyLog, b["id"]).qty == 300
    assert db.scalar(select(IssueNote).where(IssueNote.log_id == b["id"])) is None


def test_stage_milestone_completes_automatically(as_murugan, db):
    oid = _oid(db, "B-PO-88340")
    assert as_murugan.post("/api/logs", json=_body(db, po="B-PO-88340", stage="CUTTING", qty=7160)).status_code == 201
    m = db.scalar(select(Milestone).where(Milestone.order_id == oid, Milestone.stage_key == "CUTTING"))
    assert str(m.actual_date) == "2026-11-03"


def test_sup_cards(as_murugan, db):
    cards = as_murugan.get("/api/sup/orders").json()
    c = next(x for x in cards if x["poNo"] == "B-PO-88213" and x["stageKey"] == "STITCHING")
    assert c["done"] == 6800 and c["neededToday"] == 520 and c["todayQty"] is None
    assert c["style"] == "Men's crew neck tee, navy"
    assert all(x["poNo"] != "B-PO-88240" for x in cards)  # other unit's order never listed
    as_murugan.post("/api/logs", json=_body(db, qty=480))
    again = next(x for x in as_murugan.get("/api/sup/orders").json()
                 if x["poNo"] == "B-PO-88213" and x["stageKey"] == "STITCHING")
    assert again["todayQty"] == 480 and again["done"] == 7280


def test_cards_hide_completed_stages(as_murugan, db):
    assert all(c["stageKey"] != "CUTTING" for c in as_murugan.get("/api/sup/orders").json()
               if c["poNo"] == "B-PO-88213")
