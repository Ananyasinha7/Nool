from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import Field, model_validator

from backend.app.schemas.common import CamelModel, OrderHealth, StageKey

ReasonCode = Literal["BUYER_REQUEST", "MATERIAL_DELAY", "CAPACITY", "OTHER"]


class OrderLineIn(CamelModel):
    size: str = Field(min_length=1, max_length=16)
    qty: int = Field(gt=0, le=1_000_000)


class OrderCreate(CamelModel):
    po_no: str = Field(min_length=1, max_length=40)
    buyer_id: str
    style: str = Field(min_length=1, max_length=120)
    colour: str = Field(min_length=1, max_length=60)
    unit_id: str
    print_unit_id: str | None = None
    wash_unit_id: str | None = None
    has_print: bool = False
    has_wash: bool = False
    ex_factory: date
    template_id: str
    qty: int | None = Field(default=None, gt=0, le=10_000_000)  # optional check; the sum of lines wins
    lines: list[OrderLineIn] = Field(min_length=1, max_length=20)
    milestone_dates: dict[str, date] | None = None  # editable plan dates before save (FR-04)

    @model_validator(mode="after")
    def _unique_sizes(self) -> OrderCreate:
        sizes = [line.size for line in self.lines]
        if len(sizes) != len(set(sizes)):
            raise ValueError("Each size can appear once.")
        return self


class MilestoneOut(CamelModel):
    id: str
    name: str
    kind: Literal["STAGE", "MANUAL"]
    stage_key: StageKey | None
    planned_date: date
    actual_date: date | None
    sort_order: int


class AssignmentOut(CamelModel):
    stage_key: StageKey
    unit_id: str
    unit_name: str


class OrderLineOut(CamelModel):
    size: str
    qty: int


class OrderDetail(CamelModel):
    id: str
    po_no: str
    buyer_id: str
    buyer_name: str
    style: str
    colour: str
    qty: int
    has_print: bool
    has_wash: bool
    ex_factory: date
    ex_factory_original: date
    template_id: str
    lines: list[OrderLineOut]
    milestones: list[MilestoneOut]
    assignments: list[AssignmentOut]
    health: OrderHealth
    open_warning: bool


class CreatedOut(CamelModel):
    id: str


class ExFactoryChangeIn(CamelModel):
    to_date: date
    reason_code: ReasonCode
    reason_text: str | None = Field(default=None, max_length=300)


class ExFactoryChangeOut(CamelModel):
    id: str
    from_date: date
    to_date: date
    reason_code: ReasonCode
    reason_text: str | None
    changed_by_name: str
    changed_at: datetime


class MilestonePatch(CamelModel):
    actual_date: date | None


class TnaItemOut(CamelModel):
    name: str
    kind: Literal["STAGE", "MANUAL"]
    stage_key: StageKey | None
    offset_days: int
    print_only: bool


class TnaTemplateOut(CamelModel):
    id: str
    name: str
    items: list[TnaItemOut]


class LookupOption(CamelModel):
    id: str
    name: str


class Lookups(CamelModel):
    buyers: list[LookupOption]
    units: list[LookupOption]
    ship_weeks: list[str]


class LogRow(CamelModel):
    id: str
    log_date: date
    stage_key: StageKey
    qty: int
    entered_by: str
    photo_ids: list[str]
    shared_photo_ids: list[str]  # which of photo_ids the buyer can see (FR-23)


class LogAck(CamelModel):
    id: str
    effective: bool
