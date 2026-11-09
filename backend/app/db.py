"""Engine and session dependency. NullPool on prod because serverless functions
must not hold pooled connections open (Neon already pools)."""
from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from backend.app.config import get_settings


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    s = get_settings()
    if not s.database_url:
        raise RuntimeError("DATABASE_URL is not set (see .env.example)")
    if s.env == "prod":
        kwargs = {"poolclass": NullPool}
    else:
        # Avoid pool_pre_ping SELECT 1 round-trip penalty (400-500ms) on each checkout.
        # Recycle every 5 minutes to prevent stale dropped sockets.
        kwargs = {"pool_size": 10, "max_overflow": 10, "pool_recycle": 300, "pool_pre_ping": False}
    return create_engine(s.database_url, **kwargs)


def get_sessionmaker() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


def get_db() -> Iterator[Session]:
    with get_sessionmaker()() as session:
        yield session
