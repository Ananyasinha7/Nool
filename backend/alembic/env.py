"""Alembic environment. Uses DIRECT_URL (non-pooled) when set: DDL and
advisory locks do not work reliably through a transaction pooler."""
from __future__ import annotations

import os

from alembic import context
from sqlalchemy import create_engine

from backend.app.models import Base

target_metadata = Base.metadata


def _url() -> str:
    url = os.environ.get("DIRECT_URL") or os.environ.get("DATABASE_URL")
    if not url:
        from backend.app.config import get_settings

        s = get_settings()
        url = s.direct_url or s.database_url
    if not url:
        raise RuntimeError("Set DATABASE_URL (and optionally DIRECT_URL) in .env")
    return url


def run_migrations_offline() -> None:
    context.configure(url=_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(_url())
    with engine.connect() as conn:
        context.configure(connection=conn, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
