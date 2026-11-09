"""Failed-login lockout: 5 failures lock the account for 10 minutes (FR-01)."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from backend.app.config import get_config
from backend.app.models import User


def minutes_locked(user: User, now: datetime | None = None) -> int:
    """Minutes remaining (rounded up), 0 when not locked."""
    now = now or datetime.now(UTC)
    if user.locked_until and user.locked_until > now:
        return max(1, -(-int((user.locked_until - now).total_seconds()) // 60))
    return 0


def register_failure(user: User, now: datetime | None = None) -> None:
    cfg = get_config()
    now = now or datetime.now(UTC)
    user.failed_logins = (user.failed_logins or 0) + 1
    if user.failed_logins >= cfg.max_failed_logins:
        user.locked_until = now + timedelta(minutes=cfg.lockout_min)
        user.failed_logins = 0


def reset(user: User) -> None:
    user.failed_logins = 0
    user.locked_until = None
