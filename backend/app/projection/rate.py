"""Weighted run-rate (D-05). Days with no log are unknown, never zero (A-16)."""
from __future__ import annotations

from collections.abc import Sequence

from backend.app.config import get_config


def weighted_rate(latest_first: Sequence[int], weights: Sequence[int] | None = None) -> float:
    """Weighted mean of the most recent logs; weights apply latest first.

    Only the logs present are used, so a single log is just that log.
    """
    w = tuple(weights) if weights is not None else get_config().rate_weights
    used = list(latest_first)[: len(w)]
    if not used:
        return 0.0
    num = sum(wt * q for wt, q in zip(w, used, strict=False))
    den = sum(w[: len(used)])
    return num / den
