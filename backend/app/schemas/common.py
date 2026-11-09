"""Contract models shared by many routes (Doc3 section 5.3). JSON is camelCase."""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="forbid")


StageKey = Literal["CUTTING", "PRINTING", "STITCHING", "WASHING", "FINISHING", "PACKING"]
Health = Literal["GREEN", "AMBER", "RED", "GREY"]
Role = Literal["MERCHANDISER", "SUPERVISOR"]
NoteCategory = Literal[
    "MACHINE_BREAKDOWN", "POWER_CUT", "ABSENTEEISM", "MATERIAL_SHORTAGE", "QUALITY_REWORK",
    "SUBCONTRACTOR_DELAY", "APPROVAL_PENDING", "OTHER", "NEEDS_REVIEW",
]


class OrderHealth(CamelModel):
    """Output of app/projection (FR-10, 11, 13)."""
    order_id: str
    health: Health
    active_stage: StageKey | None
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


class OrderSummary(CamelModel):
    id: str
    po_no: str
    buyer_name: str
    style: str
    colour: str
    qty: int
    ex_factory: date
    unit_name: str
    health: OrderHealth
    open_warning: bool


class LogInput(CamelModel):
    id: str = Field(pattern=r"^[0-9a-fA-F-]{36}$")  # client UUID = idempotency key
    order_id: str
    stage_key: StageKey
    log_date: date
    qty: int = Field(ge=0, le=1_000_000)
    note_text: str | None = Field(default=None, max_length=500)
    client_created_at: datetime


class SupOrderCard(CamelModel):
    order_id: str
    po_no: str
    style: str
    stage_key: StageKey
    qty: int
    done: int
    needed_today: int
    today_qty: int | None


class NoteView(CamelModel):
    id: str
    original_text: str
    lang: Literal["ta", "en"]
    translation_en: str
    category: NoteCategory
    confidence: float | None
    source: Literal["AI", "RULE", "HUMAN"]
    needs_review: bool


class BuyerPreview(CamelModel):
    category: NoteCategory
    ship_slip_days: int
    text: str


class WarningView(CamelModel):
    id: str
    order_id: str
    po_no: str
    health: Health
    snapshot: OrderHealth
    note: NoteView | None
    status: Literal["DRAFT", "CONFIRMED", "DISMISSED"]
    buyer_preview: BuyerPreview


class ApiErrorBody(CamelModel):
    code: Literal["VALIDATION", "UNAUTHENTICATED", "FORBIDDEN", "NOT_FOUND", "CONFLICT",
                  "RATE_LIMITED", "SERVER"]
    message: str
    fields: dict[str, str] | None = None


class ApiError(CamelModel):
    error: ApiErrorBody
