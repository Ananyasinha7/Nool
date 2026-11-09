"""Plain dataclasses so the projection stays free of pydantic/FastAPI/SQLAlchemy."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class StageInput:
    key: str                       # CUTTING ... PACKING, already in flow order
    deadline: date                 # TNA deadline for this stage
    window_start: date             # planned start, used for the planned rate (A-18)
    done: int                      # sum of effective logs
    logs: tuple[tuple[date, int], ...] = ()   # effective (log_date, qty), any order


@dataclass(frozen=True)
class HealthInput:
    order_id: str
    qty: int
    ex_factory: date
    stages: tuple[StageInput, ...]
    holidays: frozenset[date] = field(default_factory=frozenset)


@dataclass(frozen=True)
class OrderHealthResult:
    """Same field names as schemas.OrderHealth (snake_case) so it maps 1:1."""
    order_id: str
    health: str
    active_stage: str | None
    qty: int
    done: int
    remaining: int
    required_per_day: float | None
    actual_per_day: float
    working_days_left: int
    overdue: bool
    stage_deadline: date
    projected_finish: date
    stage_slip_days: int
    projected_ship_date: date
    ship_slip_days: int
    projected_at_deadline: int
    ratio: float
    low_confidence: bool
    stale: bool
    last_log_date: date | None
    lead_days: int
    recovery_per_day: int
