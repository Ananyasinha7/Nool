"""One place that answers 'what is today?' so seeded colours stay stable (A-13)."""
from __future__ import annotations

from datetime import date

from backend.app.config import get_settings


def get_today() -> date:
    fixed = get_settings().demo_today
    return date.fromisoformat(fixed) if fixed else date.today()
