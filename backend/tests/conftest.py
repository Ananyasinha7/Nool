"""Shared fixtures. DB-backed tests need TEST_DATABASE_URL pointing at a THROWAWAY Postgres
(never production); without it they are skipped (marked NOT RUN in the build report)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

TEST_DB = os.environ.get("TEST_DATABASE_URL", "")
os.environ.setdefault("DEMO_TODAY", "2026-11-03")
os.environ.setdefault("AI_MODE", "mock")
os.environ.setdefault("JWT_SECRET", "test-secret-test-secret-test-secret-1234")
if TEST_DB:
    os.environ["DATABASE_URL"] = TEST_DB
    os.environ["DIRECT_URL"] = TEST_DB


@pytest.fixture(scope="session")
def pg_engine():
    """Clean schema built by the real Alembic chain, seeded once."""
    if not TEST_DB:
        pytest.skip("TEST_DATABASE_URL not set (needs a throwaway Postgres)")
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import Session

    engine = create_engine(TEST_DB)
    with engine.begin() as c:
        c.execute(text("DROP SCHEMA public CASCADE"))
        c.execute(text("CREATE SCHEMA public"))
    cfg = Config(str(ROOT / "backend" / "alembic.ini"))
    command.upgrade(cfg, "head")

    from backend.seed.orders import seed_orders
    from backend.seed.reference import seed_reference

    with Session(engine) as s:
        ids = seed_reference(s)
        seed_orders(s, ids)
        s.commit()
    yield engine
    engine.dispose()


@pytest.fixture()
def db(pg_engine):
    """Per-test session inside a rolled-back outer transaction (commits become savepoints)."""
    from sqlalchemy.orm import Session

    conn = pg_engine.connect()
    outer = conn.begin()
    session = Session(bind=conn, join_transaction_mode="create_savepoint", expire_on_commit=False)
    yield session
    session.close()
    outer.rollback()
    conn.close()


@pytest.fixture()
def client(db):
    """TestClient whose requests share the rolled-back test session."""
    from fastapi.testclient import TestClient

    from backend.app.db import get_db
    from backend.app.main import app

    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def login(client, username: str, secret: str):
    return client.post("/api/auth/login", json={"username": username, "password": secret})


@pytest.fixture()
def as_priya(client):
    assert login(client, "priya.merch", "Nool@Demo2026").status_code == 200
    return client


@pytest.fixture()
def as_murugan(client):
    assert login(client, "murugan.u1", "246810").status_code == 200
    return client


def buyer_client(client, token: str):
    r = client.post("/api/buyer/session", json={"token": token})
    assert r.status_code == 200, r.text
    return client
