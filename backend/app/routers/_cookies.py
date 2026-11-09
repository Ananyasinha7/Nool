from __future__ import annotations

from fastapi import Response

from backend.app.auth.tokens import COOKIE_NAME, Principal, issue_token, session_days
from backend.app.config import get_settings


def set_session(response: Response, principal: Principal) -> None:
    response.set_cookie(
        COOKIE_NAME, issue_token(principal), max_age=session_days(principal.role) * 86400, httponly=True,
        secure=get_settings().env == "prod", samesite="lax", path="/")


def clear_session(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/")
