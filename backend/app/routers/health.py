from __future__ import annotations

import time
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from backend.app.clock import get_today
from backend.app.db import get_engine

router = APIRouter(tags=["health"])

_last_db_check: float = 0.0
_last_db_ok: bool = True


class Healthz(BaseModel):
    ok: bool
    db: bool
    today: str  # the server's date (demo clock aware): phones date their entries with this, not the device clock


@router.get("/healthz", response_model=Healthz)
def healthz() -> Healthz:
    global _last_db_check, _last_db_ok
    now = time.time()
    # Cache DB check for 30s to avoid 500-1500ms round-trip tax on every client startup / route load
    if now - _last_db_check > 30.0:
        try:
            with get_engine().connect() as c:
                c.execute(text("SELECT 1"))
            _last_db_ok = True
        except Exception:
            _last_db_ok = False
        _last_db_check = now
    return Healthz(ok=True, db=_last_db_ok, today=get_today().isoformat())
