import io
import uuid

from PIL import Image
from sqlalchemy import select

from backend.app.models import IssueNote, Order, OutboxMessage, Warning


def _draft(db, po):
    oid = db.scalar(select(Order.id).where(Order.po_no == po))
    return db.scalar(select(Warning).where(Warning.order_id == oid, Warning.status == "DRAFT"))


def test_inbox_lists_seeded_drafts_with_maths_and_note(as_priya):
    rows = as_priya.get("/api/warnings").json()
    assert {r["poNo"] for r in rows} == {"B-PO-88240", "B-PO-88301"}
    r = next(x for x in rows if x["poNo"] == "B-PO-88240")
    assert r["snapshot"]["workingDaysLeft"] == 6 and r["note"]["originalText"] == "2 தையல் மெசின் பழுது"
    assert r["note"]["translationEn"] and r["note"]["needsReview"] is False
    assert r["buyerPreview"]["text"].startswith("Delay notice · Machine breakdown")


def test_confirm_writes_outbox_and_freezes(as_priya, db):
    w = _draft(db, "B-PO-88240")
    before = db.query(OutboxMessage).count()
    r = as_priya.post(f"/api/warnings/{w.id}/confirm", json={"category": "MACHINE_BREAKDOWN"})
    assert r.status_code == 200 and r.json()["status"] == "CONFIRMED"
    assert db.query(OutboxMessage).count() == before + 1
    assert as_priya.post(f"/api/warnings/{w.id}/confirm", json={"category": "OTHER"}).status_code == 409


def test_confirm_with_changed_category_marks_human(as_priya, db):
    w = _draft(db, "B-PO-88301")
    as_priya.post(f"/api/warnings/{w.id}/confirm", json={"category": "MACHINE_BREAKDOWN"})
    note = db.get(IssueNote, w.note_id)
    assert note.category == "MACHINE_BREAKDOWN" and note.source == "HUMAN" and note.reviewed_by_id


def test_needs_review_category_not_accepted(as_priya, db):
    w = _draft(db, "B-PO-88240")
    assert as_priya.post(f"/api/warnings/{w.id}/confirm", json={"category": "NEEDS_REVIEW"}).status_code == 422


def test_dismiss(as_priya, db):
    w = _draft(db, "B-PO-88240")
    assert as_priya.post(f"/api/warnings/{w.id}/dismiss").json()["status"] == "DISMISSED"
    assert all(x["poNo"] != "B-PO-88240" for x in as_priya.get("/api/warnings").json())


def test_note_category_patch_is_human(as_priya, db):
    n = db.scalar(select(IssueNote))
    r = as_priya.patch(f"/api/notes/{n.id}", json={"category": "OTHER"})
    assert r.status_code == 200 and r.json()["source"] == "HUMAN"


def test_outbox_lists_seed_rows(as_priya):
    rows = as_priya.get("/api/outbox").json()
    assert rows and {"to", "subject", "body", "createdAt"} <= set(rows[0])


def _jpeg():
    b = io.BytesIO()
    Image.new("RGB", (40, 30), (10, 200, 10)).save(b, "JPEG")
    return b.getvalue()


def test_photo_upload_idempotent_and_served(as_murugan, db):
    from backend.app.models import DailyLog

    oid = db.scalar(select(Order.id).where(Order.po_no == "B-PO-88213"))
    log = db.scalar(select(DailyLog).where(DailyLog.order_id == oid, DailyLog.superseded_by_id.is_(None)))
    pid = str(uuid.uuid4())
    files = lambda: {"file": ("a.jpg", _jpeg(), "image/jpeg")}  # noqa: E731
    r1 = as_murugan.post(f"/api/logs/{log.id}/photo", data={"photoId": pid}, files=files())
    r2 = as_murugan.post(f"/api/logs/{log.id}/photo", data={"photoId": pid}, files=files())
    assert (r1.status_code, r2.status_code) == (201, 200)
    got = as_murugan.get(f"/api/photos/{pid}")
    assert got.status_code == 200 and got.headers["content-type"] == "image/jpeg"
    assert "private" in got.headers["cache-control"]


def test_photo_rejects_non_image_and_oversize(as_murugan, db):
    from backend.app.models import DailyLog

    oid = db.scalar(select(Order.id).where(Order.po_no == "B-PO-88213"))
    log = db.scalar(select(DailyLog).where(DailyLog.order_id == oid, DailyLog.superseded_by_id.is_(None)))
    bad = as_murugan.post(f"/api/logs/{log.id}/photo", data={"photoId": str(uuid.uuid4())},
                          files={"file": ("a.jpg", b"<script>alert(1)</script>", "image/jpeg")})
    assert bad.status_code == 422  # declared type is not trusted
    big = as_murugan.post(f"/api/logs/{log.id}/photo", data={"photoId": str(uuid.uuid4())},
                          files={"file": ("a.jpg", b"0" * 500_000, "image/jpeg")})
    assert big.status_code == 413


def test_merch_toggles_sharing(as_priya, db):
    from backend.app.models import Photo

    p = db.scalar(select(Photo).where(Photo.share_with_buyer.is_(False)))
    assert as_priya.patch(f"/api/photos/{p.id}", json={"shareWithBuyer": True}).status_code == 200
    assert db.get(Photo, p.id).share_with_buyer is True
