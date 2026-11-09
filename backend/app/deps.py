"""Auth dependencies: who is calling, which role is allowed, same-origin check."""
from __future__ import annotations

from collections.abc import Callable
from urllib.parse import urlparse

from fastapi import Depends, Request

from backend.app.auth.tokens import COOKIE_NAME, Principal, read_token
from backend.app.config import get_settings
from backend.app.errors import AppError

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def current_principal(request: Request) -> Principal:
    token = request.cookies.get(COOKIE_NAME)
    principal = read_token(token) if token else None
    if principal is None:
        raise AppError(401, "Please sign in.")
    return principal


def require_role(*roles: str) -> Callable[..., Principal]:
    def dep(p: Principal = Depends(current_principal)) -> Principal:
        if p.role not in roles:
            raise AppError(403, "You do not have access to this.")
        return p

    return dep


def check_origin(request: Request) -> None:
    """CSRF defence on top of SameSite=Lax: a state-changing request that carries an Origin
    must come from this site. Requests without Origin (non-browser clients) rely on the cookie."""
    if request.method in SAFE_METHODS:
        return
    origin = request.headers.get("origin")
    if not origin:
        return
    s = get_settings()
    origin_netloc = urlparse(origin).netloc
    allowed = {
        request.headers.get("host", ""),
        request.headers.get("x-forwarded-host", ""),
        urlparse(s.app_url).netloc,
    }
    if s.env == "dev":
        # In local development, allow testing from mobile devices on the same local network
        origin_host = origin_netloc.split(":")[0]
        if (
            origin_host in ("localhost", "127.0.0.1")
            or origin_host.startswith(("192.168.", "10.", "172."))
        ):
            return
    if origin_netloc not in allowed:
        raise AppError(403, "Cross-site request blocked.")
