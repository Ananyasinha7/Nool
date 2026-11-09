import uuid

from sqlalchemy import select

from backend.app.ai import groq_client
from backend.app.models import DailyLog, IssueNote, Order


def _log(db):
    oid = db.scalar(select(Order.id).where(Order.po_no == "B-PO-88329"))
    return db.scalar(select(DailyLog).where(DailyLog.order_id == oid, DailyLog.superseded_by_id.is_(None)))


def _body(db, qty=300):
    return {"id": str(uuid.uuid4()), "orderId": _log(db).order_id, "stageKey": "STITCHING", "logDate": "2026-11-03",
            "qty": qty, "clientCreatedAt": "2026-11-03T06:00:00Z"}


def test_voice_note_is_transcribed_and_classified(as_murugan, db, monkeypatch):
    monkeypatch.setattr(groq_client, "transcribe", lambda *a, **k: "நீல நிற துணி வரவில்லை")
    b = _body(db)
    as_murugan.post("/api/logs", json=b)
    r = as_murugan.post(f"/api/logs/{b['id']}/audio", files={"file": ("n.webm", b"fake-audio", "audio/webm")})
    assert r.status_code == 201
    note = db.scalar(select(IssueNote).where(IssueNote.log_id == b["id"]))
    assert note.category == "MATERIAL_SHORTAGE"


def test_transcription_failure_keeps_numbers_and_flags_review(as_murugan, db, monkeypatch):
    def boom(*a, **k):
        raise groq_client.GroqError("down")

    monkeypatch.setattr(groq_client, "transcribe", boom)
    b = _body(db, qty=310)
    as_murugan.post("/api/logs", json=b)
    assert as_murugan.post(f"/api/logs/{b['id']}/audio",
                           files={"file": ("n.webm", b"x", "audio/webm")}).status_code == 201
    assert db.get(DailyLog, b["id"]).qty == 310
    note = db.scalar(select(IssueNote).where(IssueNote.log_id == b["id"]))
    assert note.category == "NEEDS_REVIEW" and "could not be transcribed" in note.original_text


def test_audio_retry_makes_no_duplicate(as_murugan, db, monkeypatch):
    monkeypatch.setattr(groq_client, "transcribe", lambda *a, **k: "15 ஆட்கள் வரவில்லை")
    b = _body(db, qty=320)
    as_murugan.post("/api/logs", json=b)
    f = {"file": ("n.webm", b"x", "audio/webm")}
    assert as_murugan.post(f"/api/logs/{b['id']}/audio", files=f).status_code == 201
    assert as_murugan.post(f"/api/logs/{b['id']}/audio", files=f).status_code == 200
    assert len(db.scalars(select(IssueNote).where(IssueNote.log_id == b["id"])).all()) == 1


def test_audio_is_not_persisted_anywhere(as_murugan, db, monkeypatch):
    monkeypatch.setattr(groq_client, "transcribe", lambda *a, **k: "machine problem")
    b = _body(db, qty=330)
    as_murugan.post("/api/logs", json=b)
    as_murugan.post(f"/api/logs/{b['id']}/audio", files={"file": ("n.webm", b"SECRET-AUDIO-BYTES", "audio/webm")})
    from sqlalchemy import text

    for table in ("photo_blobs", "issue_notes", "ai_cache"):
        assert "SECRET-AUDIO-BYTES" not in str(db.execute(text(f"select * from {table}")).fetchall())


def test_other_units_entry_forbidden(as_murugan, db):
    oid = db.scalar(select(Order.id).where(Order.po_no == "B-PO-88240"))
    other = db.scalar(select(DailyLog).where(DailyLog.order_id == oid))
    assert as_murugan.post(f"/api/logs/{other.id}/audio", files={"file": ("n.webm", b"x", "audio/webm")}
                           ).status_code == 403
