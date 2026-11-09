"""FastAPI app. Routers mount under /api so the same code works behind the Vercel rewrite."""
from __future__ import annotations

from fastapi import Depends, FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.config import get_settings
from backend.app.deps import check_origin
from backend.app.errors import install_handlers
from backend.app.routers import (
    audio,
    auth,
    buyer,
    buyer_links,
    export,
    health,
    logs,
    milestones,
    notes,
    orders,
    outbox,
    photos,
    sup,
    warnings,
)


class SecurityHeaders(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["X-Frame-Options"] = "DENY"
        return response


def _assert_safe_config() -> None:
    """Refuse to start in production with a guessable signing key: every session cookie depends on it."""
    s = get_settings()
    if s.env == "prod" and (s.jwt_secret.startswith("dev-only") or len(s.jwt_secret) < 32):
        raise RuntimeError("JWT_SECRET must be set to 32+ random characters when ENV=prod")


def create_app() -> FastAPI:
    _assert_safe_config()
    dev = get_settings().env == "dev"
    app = FastAPI(
        title="Nool API", version="1.0.0",
        docs_url="/docs" if dev else None, redoc_url=None, openapi_url="/openapi.json" if dev else None,
        dependencies=[Depends(check_origin)],
    )
    app.add_middleware(SecurityHeaders)
    install_handlers(app)
    modules = (health, auth, audio, orders, milestones, logs, sup, photos, notes, warnings, outbox, buyer_links, buyer,
               export)
    for module in modules:
        app.include_router(module.router, prefix="/api")
    return app


app = create_app()
