from datetime import UTC, datetime, timedelta

from backend.app.auth.lockout import minutes_locked, register_failure, reset
from backend.app.auth.passwords import hash_password, verify_password
from backend.app.auth.tokens import Principal, issue_token, read_token
from backend.app.models import User


def test_password_roundtrip_and_unknown_user():
    h = hash_password("s3cret")
    assert verify_password("s3cret", h) and not verify_password("nope", h)
    assert not verify_password("anything", None)  # unknown user is always a failure


def test_token_roundtrip_and_tamper():
    t = issue_token(Principal(role="SUPERVISOR", user_id="u1", unit_id="x"))
    p = read_token(t)
    assert p and p.role == "SUPERVISOR" and p.unit_id == "x"
    assert read_token(t[:-2] + "xx") is None
    assert read_token("garbage") is None


def test_expired_token_rejected():
    old = datetime.now(UTC) - timedelta(days=400)
    assert read_token(issue_token(Principal(role="MERCHANDISER", user_id="u"), now=old)) is None


def test_lockout_after_five_failures():
    u = User(username="x", display_name="x", password_hash="h", role="SUPERVISOR", failed_logins=0)
    now = datetime(2026, 11, 3, 10, tzinfo=UTC)
    for _ in range(4):
        register_failure(u, now)
    assert minutes_locked(u, now) == 0
    register_failure(u, now)
    assert minutes_locked(u, now) == 10
    assert minutes_locked(u, now + timedelta(minutes=11)) == 0
    reset(u)
    assert u.failed_logins == 0 and u.locked_until is None
