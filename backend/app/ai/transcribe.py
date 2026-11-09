"""Voice note -> text -> the same classifier (Doc3 section 11, FR-25). Audio is never stored (TD-6)."""
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from backend.app.ai import groq_client
from backend.app.models import DailyLog, IssueNote
from backend.app.services.notes import attach_note

log = logging.getLogger("nool")
FAILED_TEXT = "voice note could not be transcribed"


def transcribe_note(session: Session, daily_log: DailyLog, audio: bytes, user_id: str | None) -> IssueNote | None:
    """The log already stands; a failure here only produces a note flagged for manual review."""
    try:
        text = groq_client.transcribe(audio)
    except groq_client.GroqError:
        text = ""
    except Exception:  # never let the audio path break the request
        log.exception("transcription crashed")
        text = ""
    if not text:
        note = IssueNote(log_id=daily_log.id, order_id=daily_log.order_id, original_text=FAILED_TEXT, lang="en",
                         translation_en="", category="NEEDS_REVIEW", confidence=None, source="RULE")
        session.add(note)
        session.flush()
        return note
    return attach_note(session, daily_log, text, user_id)
