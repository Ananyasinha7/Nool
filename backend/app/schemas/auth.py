from __future__ import annotations

from typing import Literal

from pydantic import Field

from backend.app.schemas.common import CamelModel


class LoginRequest(CamelModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class MeOut(CamelModel):
    role: Literal["MERCHANDISER", "SUPERVISOR", "BUYER"]
    display_name: str
    lang: Literal["en", "ta"]
    unit_id: str | None = None
    unit_name: str | None = None
    buyer_name: str | None = None


class MePatch(CamelModel):
    lang: Literal["en", "ta"]


class OkOut(CamelModel):
    ok: bool = True
