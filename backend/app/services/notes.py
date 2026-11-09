"""Turns a log's free text into a classified IssueNote, after the numbers are committed (F-1)."""
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from backend.app.ai.classify import classify
from backend.app.models import DailyLog, IssueNote
from backend.app.services.warnings import open_draft

log = logging.getLogger("nool")


def detect_lang(text: str) -> str:
    return "ta" if any("\u0b80" <= ch <= "\u0bff" for ch in text) else "en"


def attach_note(session: Session, daily_log: DailyLog, text: str, user_id: str | None) -> IssueNote | None:
    """Never raises: if anything fails the log (the numbers) still stands."""
    try:
        with session.begin_nested():
            out = classify(session, text, user_id)
            note = IssueNote(log_id=daily_log.id, order_id=daily_log.order_id, original_text=text,
                             lang=detect_lang(text), translation_en=out.translation_en, category=out.category,
                             confidence=out.confidence, source=out.source)
            session.add(note)
            session.flush()
            draft = open_draft(session, daily_log.order_id)
            if draft is not None:
                draft.note_id = note.id
        return note
    except Exception:
        log.exception("note classification failed; log kept")
        return None
