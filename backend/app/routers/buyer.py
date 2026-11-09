"""Read-only buyer API. Every route declares an explicit response model, so FastAPI strips any field
that is not listed (BR-05): no units, supervisor names, internal notes or unconfirmed warnings."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.auth.tokens import Principal
from backend.app.clock import get_today
from backend.app.db import get_db
from backend.app.errors import AppError
from backend.app.models import DailyLog, ExFactoryChange, Milestone, Order, Photo, User, Warning
from backend.app.routers._cookies import set_session
from backend.app.schemas.auth import OkOut
from backend.app.schemas.misc import (
    BuyerDateChange,
    BuyerDelayNotice,
    BuyerMilestone,
    BuyerOrderDetail,
    BuyerOrderView,
    BuyerPhoto,
    BuyerSessionIn,
)
from backend.app.services import buyer_links
from backend.app.services.health import build_inputs, health_for
from backend.app.services.scope import BuyerScope, buyer_scope
from backend.app.services.warnings import CATEGORY_LABEL, buyer_text

router = APIRouter(tags=["buyer"])
REASON_LABEL = {"BUYER_REQUEST": "Buyer request", "MATERIAL_DELAY": "Material delay", "CAPACITY": "Capacity",
                "OTHER": "Other"}
INVALID = "This link is no longer active. Please contact your merchandiser."


@router.post("/buyer/session", response_model=OkOut)
def start_session(body: BuyerSessionIn, response: Response, db: Session = Depends(get_db)) -> OkOut:
    link = buyer_links.resolve(db, body.token)
    if link is None:
        raise AppError(401, INVALID)  # unknown and revoked look identical: nothing leaks
    set_session(response, Principal(role="BUYER", buyer_id=link.buyer_id, link_id=link.id))
    return OkOut()


def _notices(s: Session, order_ids: list[str]) -> dict[str, BuyerDelayNotice]:
    """Only CONFIRMED warnings ever reach a buyer (FR-17); latest per order. Category label and date
    impact only, never the raw note (D-17)."""
    out: dict[str, BuyerDelayNotice] = {}
    rows = s.scalars(select(Warning).where(Warning.order_id.in_(order_ids), Warning.status == "CONFIRMED")
                     .order_by(Warning.confirmed_at))
    for w in rows:
        cat = w.category_final or "OTHER"
        slip = int(w.snapshot.get("shipSlipDays", 0))
        out[w.order_id] = BuyerDelayNotice(category_label=CATEGORY_LABEL.get(cat, "Production issue"),
                                           ship_slip_days=slip, text=buyer_text(cat, slip),
                                           confirmed_at=w.confirmed_at)
    return out


def _views(scope: BuyerScope, orders: list[Order]) -> list[BuyerOrderView]:
    s = scope.session
    if not orders:
        return []
    ids = [o.id for o in orders]
    inputs = build_inputs(s, orders)
    health = health_for(s, orders, get_today(), inputs=inputs)
    notices = _notices(s, ids)
    out = []
    for o in orders:
        stages = inputs[o.id].stages
        pct = round(100 * sum(min(1.0, st.done / o.qty) for st in stages) / len(stages)) if stages else 0
        out.append(BuyerOrderView(id=o.id, po_no=o.po_no, style=o.style, colour=o.colour, qty=o.qty,
                                  ex_factory=o.ex_factory, progress_pct=pct,
                                  current_stage=health[o.id].active_stage, delay_notice=notices.get(o.id)))
    return out


@router.get("/buyer/orders", response_model=list[BuyerOrderView])
def buyer_orders(scope: BuyerScope = Depends(buyer_scope)) -> list[BuyerOrderView]:
    orders = list(scope.session.scalars(scope.order_query().order_by(Order.ex_factory)))
    return _views(scope, orders)


@router.get("/buyer/orders/{order_id}", response_model=BuyerOrderDetail)
def buyer_order(order_id: str, scope: BuyerScope = Depends(buyer_scope)) -> BuyerOrderDetail:
    s = scope.session
    order = scope.get_order(order_id)  # a foreign id is a 404
    view = _views(scope, [order])[0]
    miles = s.scalars(select(Milestone).where(Milestone.order_id == order.id).order_by(Milestone.sort_order))
    photos = s.execute(select(Photo.id, DailyLog.log_date).join(DailyLog, DailyLog.id == Photo.log_id)
                       .where(DailyLog.order_id == order.id, Photo.share_with_buyer.is_(True))
                       .order_by(DailyLog.log_date.desc(), Photo.created_at.desc())).all()
    changes = s.execute(select(ExFactoryChange, User.display_name).join(User, User.id == ExFactoryChange.changed_by_id)
                        .where(ExFactoryChange.order_id == order.id).order_by(ExFactoryChange.changed_at)).all()
    return BuyerOrderDetail(
        **view.model_dump(),
        milestones=[BuyerMilestone(name=m.name, planned_date=m.planned_date, actual_date=m.actual_date)
                    for m in miles],
        photos=[BuyerPhoto(id=pid, taken_on=d, url=f"/api/photos/{pid}") for pid, d in photos],
        date_history=[BuyerDateChange(changed_at=c.changed_at, from_date=c.from_date, to_date=c.to_date,
                                      reason=REASON_LABEL.get(c.reason_code, "Other")
                                      + (f": {c.reason_text}" if c.reason_text else ""), changed_by=name)
                      for c, name in changes])
