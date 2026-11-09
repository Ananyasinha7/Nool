from __future__ import annotations

from fastapi import APIRouter, Depends, File, Response, UploadFile
from sqlalchemy import select

from backend.app.ai.transcribe import transcribe_note
from backend.app.errors import AppError
from backend.app.models import DailyLog, IssueNote
from backend.app.schemas.auth import OkOut
from backend.app.services.scope import SupervisorScope, sup_scope

router = APIRouter(tags=["audio"])
MAX_AUDIO_BYTES = 1_500_000  # ~30 s of opus with generous headroom (audioMaxSeconds in config.json)


@router.post("/logs/{log_id}/audio", response_model=OkOut, status_code=201)
def upload_audio(log_id: str, response: Response, file: UploadFile = File(...),
                 scope: SupervisorScope = Depends(sup_scope)) -> OkOut:
    s = scope.session
    log = s.get(DailyLog, log_id)
    if log is None or log.entered_by_id != scope.principal.user_id:
        raise AppError(403, "You do not have access to this entry.")
    scope.get_order(log.order_id)
    if s.scalar(select(IssueNote.id).where(IssueNote.log_id == log_id)):
        response.status_code = 200  # a log keeps one note; a retry is harmless
        return OkOut()
    data = file.file.read(MAX_AUDIO_BYTES + 1)
    if not data or len(data) > MAX_AUDIO_BYTES:
        raise AppError(413, "Voice note is empty or too long.", {"file": "Voice note is empty or too long."})
    transcribe_note(s, log, data, scope.principal.user_id)  # audio bytes are dropped after this call
    s.commit()
    return OkOut()
