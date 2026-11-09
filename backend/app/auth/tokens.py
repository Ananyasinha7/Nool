"""Signed session cookie (PyJWT HS256). The payload carries role, user id and buyer id."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt

from backend.app.config import get_config, get_settings

COOKIE_NAME = "nool_session"
ALGORITHM = "HS256"


@dataclass(frozen=True)
class Principal:
    role: str                      # MERCHANDISER | SUPERVISOR | BUYER
    user_id: str | None = None
    unit_id: str | None = None
    buyer_id: str | None = None
    link_id: str | None = None     # buyer sessions: re-checked on every request so revoking is immediate


def session_days(role: str) -> int:
    return get_config().session_days[role]


def issue_token(p: Principal, now: datetime | None = None) -> str:
    now = now or datetime.now(UTC)
    payload = {
        "role": p.role, "uid": p.user_id, "unit": p.unit_id, "buyer": p.buyer_id, "lnk": p.link_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=session_days(p.role))).timestamp()),
    }
    return jwt.encode(payload, get_settings().jwt_secret, algorithm=ALGORITHM)


def read_token(token: str) -> Principal | None:
    """None for any invalid, tampered or expired token (callers answer 401)."""
    try:
        data = jwt.decode(token, get_settings().jwt_secret, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
    if data.get("role") not in ("MERCHANDISER", "SUPERVISOR", "BUYER"):
        return None
    return Principal(role=data["role"], user_id=data.get("uid"), unit_id=data.get("unit"),
                     buyer_id=data.get("buyer"),
                     link_id=data.get("lnk"))
