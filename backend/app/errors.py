"""One error shape for everything: {error:{code,message,fields?}}. Stack traces never leave the server."""
from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

log = logging.getLogger("nool")

_CODES = {400: "VALIDATION", 401: "UNAUTHENTICATED", 403: "FORBIDDEN", 404: "NOT_FOUND", 409: "CONFLICT",
          413: "VALIDATION", 422: "VALIDATION", 429: "RATE_LIMITED"}


class AppError(HTTPException):
    """Raise with an explicit code and optional per-field messages."""

    def __init__(self, status: int, message: str, fields: dict[str, str] | None = None):
        super().__init__(status_code=status, detail=message)
        self.fields = fields


def _body(code: str, message: str, fields: dict[str, str] | None = None) -> dict:
    err: dict = {"code": code, "message": message}
    if fields:
        err["fields"] = fields
    return {"error": err}


def install_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = _CODES.get(exc.status_code, "SERVER" if exc.status_code >= 500 else "VALIDATION")
        fields = getattr(exc, "fields", None)
        return JSONResponse(_body(code, str(exc.detail), fields), status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        fields: dict[str, str] = {}
        for e in exc.errors():
            loc = [str(x) for x in e["loc"] if x not in ("body", "query", "path")]
            fields[".".join(loc) or "request"] = e["msg"]
        return JSONResponse(_body("VALIDATION", "Please check the highlighted fields.", fields), status_code=422)

    @app.exception_handler(Exception)
    async def _unexpected(_: Request, exc: Exception) -> JSONResponse:
        log.exception("unhandled error", exc_info=exc)
        return JSONResponse(_body("SERVER", "Something went wrong. Please try again."), status_code=500)
