from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import Field

from backend.app.schemas.common import CamelModel, StageKey

EditableCategory = Literal["MACHINE_BREAKDOWN", "POWER_CUT", "ABSENTEEISM", "MATERIAL_SHORTAGE", "QUALITY_REWORK",
                           "SUBCONTRACTOR_DELAY", "APPROVAL_PENDING", "OTHER"]


class CategoryIn(CamelModel):
    category: EditableCategory


class PhotoPatch(CamelModel):
    share_with_buyer: bool


class PhotoAck(CamelModel):
    id: str


class OutboxOut(CamelModel):
    id: str
    to: str
    subject: str
    body: str
    created_at: datetime


class LinkCreated(CamelModel):
    id: str
    url: str  # contains the token: shown once, only its hash is stored


class LinkOut(CamelModel):
    id: str
    label: str
    created_at: datetime
    revoked: bool


class LinkLabel(CamelModel):
    label: str = Field(default="", max_length=60)


class BuyerSessionIn(CamelModel):
    token: str = Field(min_length=8, max_length=200)


class BuyerDelayNotice(CamelModel):
    category_label: str
    ship_slip_days: int
    text: str
    confirmed_at: datetime | None


class BuyerOrderView(CamelModel):
    """Explicit allow-list: FastAPI strips everything not declared here (BR-05)."""
    id: str
    po_no: str
    style: str
    colour: str
    qty: int
    ex_factory: date
    progress_pct: int
    current_stage: StageKey | None
    delay_notice: BuyerDelayNotice | None


class BuyerMilestone(CamelModel):
    name: str
    planned_date: date
    actual_date: date | None


class BuyerPhoto(CamelModel):
    id: str
    taken_on: date
    url: str


class BuyerDateChange(CamelModel):
    changed_at: datetime
    from_date: date
    to_date: date
    reason: str
    changed_by: str


class BuyerOrderDetail(BuyerOrderView):
    milestones: list[BuyerMilestone]
    photos: list[BuyerPhoto]
    date_history: list[BuyerDateChange]
