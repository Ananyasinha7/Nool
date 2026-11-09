"""Status colours from the ratio and the projected slip (BR-03, D-06)."""
from __future__ import annotations

from backend.app.config import get_config

_ORDER = {"GREEN": 0, "GREY": 0, "AMBER": 1, "RED": 2}


def ratio_status(ratio: float) -> str:
    cfg = get_config()
    if ratio >= cfg.ratio_green:
        return "GREEN"
    if ratio >= cfg.ratio_amber:
        return "AMBER"
    return "RED"


def slip_status(stage_slip: int) -> str:
    cfg = get_config()
    if stage_slip >= cfg.slip_red_min:
        return "RED"
    if stage_slip >= cfg.slip_amber_min:
        return "AMBER"
    return "GREEN"


def worst(a: str, b: str) -> str:
    return a if _ORDER[a] >= _ORDER[b] else b


def combine(ratio: float, stage_slip: int, ship_slip: int, stale: bool) -> str:
    health = worst(ratio_status(ratio), slip_status(stage_slip))
    if ship_slip > 0 and health == "GREEN":
        health = "AMBER"
    # GREY only replaces GREEN: it must never hide amber or red.
    if stale and health == "GREEN":
        health = "GREY"
    return health
