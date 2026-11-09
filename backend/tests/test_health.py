from fastapi.testclient import TestClient

from backend.app.main import app


def test_healthz_answers_without_database():
    r = TestClient(app).get("/api/healthz")
    assert r.status_code == 200 and r.json()["ok"] is True


def test_security_headers():
    r = TestClient(app).get("/api/healthz")
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"


def test_healthz_reports_server_date():
    import re

    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", TestClient(app).get("/api/healthz").json()["today"])


def test_prod_refuses_default_signing_key(monkeypatch):
    import pytest

    from backend.app.config import get_settings
    from backend.app.main import create_app

    s = get_settings()
    monkeypatch.setattr(s, "env", "prod")
    monkeypatch.setattr(s, "jwt_secret", "dev-only-change-me-dev-only-change-me")
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        create_app()
    monkeypatch.setattr(s, "jwt_secret", "x" * 40)
    assert create_app() is not None  # a real secret is accepted
