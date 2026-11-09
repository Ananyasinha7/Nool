from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select

from backend.app.errors import AppError
from backend.app.models import Milestone, TnaTemplate
from backend.app.schemas.orders import MilestoneOut, MilestonePatch, TnaItemOut, TnaTemplateOut
from backend.app.services.audit import audit
from backend.app.services.scope import MerchScope, merch_scope

router = APIRouter(tags=["milestones"])


@router.patch("/milestones/{milestone_id}", response_model=MilestoneOut)
def patch_milestone(milestone_id: str, body: MilestonePatch, scope: MerchScope = Depends(merch_scope)):
    m = scope.session.get(Milestone, milestone_id)
    if m is None:
        raise AppError(404, "Milestone not found.")
    scope.get_order(m.order_id)  # scope check
    if m.kind != "MANUAL":
        raise AppError(409, "Stage milestones complete automatically from the daily numbers.")
    m.actual_date = body.actual_date
    audit(scope.session, scope.principal.user_id, "MILESTONE_TICKED", "milestone", m.id,
          actual=body.actual_date)  # ticking is audited (FR-05)
    scope.session.commit()
    return MilestoneOut(id=m.id, name=m.name, kind=m.kind, stage_key=m.stage_key, planned_date=m.planned_date,
                        actual_date=m.actual_date, sort_order=m.sort_order)


@router.get("/tna-templates", response_model=list[TnaTemplateOut])
def tna_templates(scope: MerchScope = Depends(merch_scope)):
    out = []
    for t in scope.session.scalars(select(TnaTemplate)):
        out.append(TnaTemplateOut(id=t.id, name=t.name, items=[
            TnaItemOut(name=i.name, kind=i.kind, stage_key=i.stage_key, offset_days=i.offset_days,
                       print_only=i.print_only) for i in t.items]))
    return out
