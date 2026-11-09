from __future__ import annotations

import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from backend.app.clock import get_today
from backend.app.db import get_sessionmaker
from backend.app.errors import AppError
from backend.app.models import (
    Buyer,
    DailyLog,
    ExFactoryChange,
    Milestone,
    Order,
    OrderLine,
    Photo,
    StageAssignment,
    Unit,
    User,
)
from backend.app.schemas.common import Health, OrderSummary
from backend.app.schemas.orders import (
    AssignmentOut,
    CreatedOut,
    ExFactoryChangeIn,
    ExFactoryChangeOut,
    LogRow,
    LookupOption,
    Lookups,
    MilestoneOut,
    OrderCreate,
    OrderDetail,
    OrderLineOut,
)
from backend.app.services import orders as svc
from backend.app.services.health import build_inputs, health_for
from backend.app.services.scope import MerchScope, merch_scope

router = APIRouter(tags=["orders"])
_SEVERITY = {"RED": 0, "AMBER": 1, "GREY": 2, "GREEN": 3}
_FLOW = ("CUTTING", "PRINTING", "STITCHING", "WASHING", "FINISHING", "PACKING")


@router.get("/orders", response_model=list[OrderSummary])
def list_orders(
    buyer_id: str | None = Query(None, alias="buyerId"), unit_id: str | None = Query(None, alias="unitId"),
    ship_week: str | None = Query(None, alias="shipWeek", pattern=r"^\d{4}-W\d{2}$"),
    status: Health | None = None, q: str | None = Query(None, max_length=60),
    scope: MerchScope = Depends(merch_scope),
) -> list[OrderSummary]:
    query = scope.order_query().options(joinedload(Order.buyer))
    if buyer_id:
        query = query.where(Order.buyer_id == buyer_id)
    if unit_id:
        query = query.where(Order.id.in_(select(StageAssignment.order_id).where(StageAssignment.unit_id == unit_id)))
    if q:
        query = query.where(Order.po_no.ilike(f"%{q.strip()}%"))
    orders = list(scope.session.scalars(query))
    if ship_week:
        orders = [o for o in orders if svc.iso_week(o.ex_factory) == ship_week]
    ids = [o.id for o in orders]
    if not ids:
        return []

    sm = get_sessionmaker()

    def fetch_miles():
        with sm() as s:
            m_map = defaultdict(list)
            q_m = select(Milestone.order_id, Milestone.stage_key, Milestone.name, Milestone.planned_date).where(
                Milestone.order_id.in_(ids)
            )
            for oid, skey, name, pdate in s.execute(q_m):
                m_map[oid].append((skey, name, pdate))
            return m_map

    def fetch_logs():
        with sm() as s:
            l_map = defaultdict(list)
            q_l = select(DailyLog.order_id, DailyLog.stage_key, DailyLog.log_date, DailyLog.qty).where(
                DailyLog.order_id.in_(ids), DailyLog.superseded_by_id.is_(None)
            )
            for oid, stage, d, qty in s.execute(q_l):
                l_map[(oid, stage)].append((d, qty))
            return l_map

    def fetch_amap():
        with sm() as s:
            return svc.assignments_map(s, ids)

    def fetch_warned():
        with sm() as s:
            return svc.open_warning_ids(s, ids)

    with ThreadPoolExecutor(max_workers=4) as pool:
        f_miles = pool.submit(fetch_miles)
        f_logs = pool.submit(fetch_logs)
        f_amap = pool.submit(fetch_amap)
        f_warned = pool.submit(fetch_warned)

        miles_data = f_miles.result()
        logs_data = f_logs.result()
        amap = f_amap.result()
        warned = f_warned.result()

    inputs = build_inputs(scope.session, orders, miles_data=miles_data, logs_data=logs_data)
    health = health_for(scope.session, orders, get_today(), inputs=inputs)
    out = []
    for o in orders:
        h = health[o.id]
        if status and h.health != status:
            continue
        stage = h.active_stage or "PACKING"
        unit_name = (amap.get(o.id, {}).get(stage) or next(iter(amap.get(o.id, {}).values()), ("", "")))[1]
        out.append(OrderSummary(id=o.id, po_no=o.po_no, buyer_name=o.buyer.name, style=o.style, colour=o.colour,
                                qty=o.qty, ex_factory=o.ex_factory, unit_name=unit_name, health=h,
                                open_warning=o.id in warned))
    # Severity, then projected slip (descending), then ship date.
    out.sort(key=lambda s: (_SEVERITY[s.health.health], -s.health.stage_slip_days, s.ex_factory))
    return out


@router.post("/orders", response_model=CreatedOut, status_code=201)
def create_order(body: OrderCreate, scope: MerchScope = Depends(merch_scope)) -> CreatedOut:
    order = svc.create_order(scope.session, body, scope.principal.user_id)
    scope.session.commit()
    return CreatedOut(id=order.id)


def _detail(scope: MerchScope, order: Order) -> OrderDetail:
    sm = get_sessionmaker()
    oid = order.id

    def fetch_miles():
        with sm() as s:
            return s.scalars(
                select(Milestone).where(Milestone.order_id == oid).order_by(Milestone.sort_order)
            ).all()

    def fetch_logs():
        with sm() as s:
            l_map = defaultdict(list)
            q_l = select(DailyLog.order_id, DailyLog.stage_key, DailyLog.log_date, DailyLog.qty).where(
                DailyLog.order_id == oid, DailyLog.superseded_by_id.is_(None)
            )
            for _, stage, d, qty in s.execute(q_l):
                l_map[(oid, stage)].append((d, qty))
            return l_map

    def fetch_lines():
        with sm() as s:
            return s.scalars(select(OrderLine).where(OrderLine.order_id == oid)).all()

    def fetch_amap():
        with sm() as s:
            return svc.assignments_map(s, [oid]).get(oid, {})

    def fetch_warned():
        with sm() as s:
            return svc.open_warning_ids(s, [oid])

    with ThreadPoolExecutor(max_workers=5) as pool:
        f_m = pool.submit(fetch_miles)
        f_l = pool.submit(fetch_logs)
        f_lines = pool.submit(fetch_lines)
        f_amap = pool.submit(fetch_amap)
        f_w = pool.submit(fetch_warned)

        miles = f_m.result()
        logs_data = f_l.result()
        lines = f_lines.result()
        amap = f_amap.result()
        warned = f_w.result()

    miles_data = {oid: [(m.stage_key, m.name, m.planned_date) for m in miles]}
    inputs = build_inputs(scope.session, [order], miles_data=miles_data, logs_data=logs_data)
    health = health_for(scope.session, [order], get_today(), inputs=inputs)[oid]

    return OrderDetail(
        id=order.id, po_no=order.po_no, buyer_id=order.buyer_id, buyer_name=order.buyer.name,
        style=order.style, colour=order.colour, qty=order.qty, has_print=order.has_print,
        has_wash=order.has_wash, ex_factory=order.ex_factory, ex_factory_original=order.ex_factory_original,
        template_id=order.template_id,
        lines=[OrderLineOut(size=ln.size, qty=ln.qty) for ln in lines],
        milestones=[MilestoneOut(id=m.id, name=m.name, kind=m.kind, stage_key=m.stage_key,
                                 planned_date=m.planned_date, actual_date=m.actual_date,
                                 sort_order=m.sort_order) for m in miles],
        assignments=[AssignmentOut(stage_key=k, unit_id=u, unit_name=n) for k, (u, n) in amap.items()],
        health=health, open_warning=oid in warned
    )


@router.get("/orders/{order_id}", response_model=OrderDetail)
def get_order(order_id: str, scope: MerchScope = Depends(merch_scope)) -> OrderDetail:
    return _detail(scope, scope.get_order(order_id))


@router.get("/orders/{order_id}/logs", response_model=list[LogRow])
def order_logs(order_id: str, days: int = Query(10, ge=1, le=60), scope: MerchScope = Depends(merch_scope)):
    order = scope.get_order(order_id)
    rows = scope.session.execute(
        select(DailyLog, User.display_name).join(User, User.id == DailyLog.entered_by_id)
        .where(DailyLog.order_id == order.id, DailyLog.superseded_by_id.is_(None))
        .order_by(DailyLog.log_date.desc(), DailyLog.stage_key)).all()
    recent_dates = sorted({lg.log_date for lg, _ in rows}, reverse=True)[:days]
    photos: dict[str, list[str]] = {}
    shared: dict[str, list[str]] = {}
    for pid, lid, is_shared in scope.session.execute(select(Photo.id, Photo.log_id, Photo.share_with_buyer).where(
            Photo.log_id.in_([lg.id for lg, _ in rows]))):
        photos.setdefault(lid, []).append(pid)
        if is_shared:
            shared.setdefault(lid, []).append(pid)
    return [LogRow(id=lg.id, log_date=lg.log_date, stage_key=lg.stage_key, qty=lg.qty, entered_by=name,
                   photo_ids=photos.get(lg.id, []),
                   shared_photo_ids=shared.get(lg.id, [])) for lg, name in rows if lg.log_date in recent_dates]


@router.patch("/orders/{order_id}/ex-factory", response_model=OrderDetail)
def change_ex_factory(order_id: str, body: ExFactoryChangeIn, scope: MerchScope = Depends(merch_scope)):
    order = scope.get_order(order_id)
    svc.change_ex_factory(scope.session, order, body.to_date, body.reason_code, body.reason_text,
                          scope.principal.user_id)
    scope.session.commit()
    return _detail(scope, order)


@router.get("/orders/{order_id}/changes", response_model=list[ExFactoryChangeOut])
def order_changes(order_id: str, scope: MerchScope = Depends(merch_scope)):
    order = scope.get_order(order_id)
    rows = scope.session.execute(
        select(ExFactoryChange, User.display_name).join(User, User.id == ExFactoryChange.changed_by_id)
        .where(ExFactoryChange.order_id == order.id).order_by(ExFactoryChange.changed_at)).all()
    return [ExFactoryChangeOut(id=c.id, from_date=c.from_date, to_date=c.to_date, reason_code=c.reason_code,
                               reason_text=c.reason_text, changed_by_name=name, changed_at=c.changed_at)
            for c, name in rows]


_cached_buyers: tuple[float, list[LookupOption]] | None = None
_cached_units: tuple[float, list[LookupOption]] | None = None


@router.get("/lookups", response_model=Lookups, tags=["lookups"])
def lookups(scope: MerchScope = Depends(merch_scope)) -> Lookups:
    global _cached_buyers, _cached_units
    s = scope.session
    now = time.time()
    if _cached_buyers is None or now - _cached_buyers[0] > 60.0:
        b_list = [LookupOption(id=b.id, name=b.name) for b in s.scalars(select(Buyer).order_by(Buyer.name))]
        _cached_buyers = (now, b_list)
    if _cached_units is None or now - _cached_units[0] > 60.0:
        u_list = [LookupOption(id=u.id, name=u.name) for u in s.scalars(select(Unit).order_by(Unit.name))]
        _cached_units = (now, u_list)
    weeks = sorted({svc.iso_week(d) for d in s.scalars(select(Order.ex_factory))})
    return Lookups(buyers=_cached_buyers[1], units=_cached_units[1], ship_weeks=weeks)


__all__ = ["router", "timedelta", "AppError"]
