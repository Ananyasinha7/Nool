"""THE scoped data layer. Routers never write a raw order query: they call a scope.
Buyer isolation (NFR-6) lives here, covered by negative tests in tests/isolation."""
from __future__ import annotations

from fastapi import Depends
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from backend.app.auth.tokens import Principal
from backend.app.db import get_db
from backend.app.deps import require_role
from backend.app.errors import AppError
from backend.app.models import Order, StageAssignment


class MerchScope:
    """Merchandisers see every order."""

    def __init__(self, session: Session, principal: Principal):
        self.session, self.principal = session, principal

    def order_query(self) -> Select[tuple[Order]]:
        return select(Order)

    def get_order(self, order_id: str) -> Order:
        order = self.session.scalar(self.order_query().where(Order.id == order_id))
        if order is None:
            raise AppError(404, "Order not found.")
        return order


class SupervisorScope:
    """Supervisors see only orders with a stage assigned to their unit (FR-06, A-10)."""

    def __init__(self, session: Session, principal: Principal):
        if not principal.unit_id:
            raise AppError(403, "No unit assigned.")
        self.session, self.principal, self.unit_id = session, principal, principal.unit_id

    def order_query(self) -> Select[tuple[Order]]:
        return select(Order).where(
            Order.id.in_(select(StageAssignment.order_id).where(StageAssignment.unit_id == self.unit_id)))

    def get_order(self, order_id: str) -> Order:
        order = self.session.scalar(self.order_query().where(Order.id == order_id))
        if order is None:
            # 403 whether or not it exists: no hint about other units' orders.
            raise AppError(403, "You do not have access to this order.")
        return order

    def assigned_stages(self, order_id: str) -> list[str]:
        return list(self.session.scalars(select(StageAssignment.stage_key).where(
            StageAssignment.order_id == order_id, StageAssignment.unit_id == self.unit_id)))


class BuyerScope:
    """Buyers see only their own company's orders; foreign ids answer 404 (FR-18)."""

    def __init__(self, session: Session, principal: Principal):
        if not principal.buyer_id:
            raise AppError(403, "Not a buyer session.")
        self.session, self.principal, self.buyer_id = session, principal, principal.buyer_id

    def order_query(self) -> Select[tuple[Order]]:
        return select(Order).where(Order.buyer_id == self.buyer_id)

    def get_order(self, order_id: str) -> Order:
        order = self.session.scalar(self.order_query().where(Order.id == order_id))
        if order is None:
            raise AppError(404, "Order not found.")
        return order


def merch_scope(db: Session = Depends(get_db), p: Principal = Depends(require_role("MERCHANDISER"))) -> MerchScope:
    return MerchScope(db, p)


def sup_scope(db: Session = Depends(get_db), p: Principal = Depends(require_role("SUPERVISOR"))) -> SupervisorScope:
    return SupervisorScope(db, p)


def buyer_scope(db: Session = Depends(get_db), p: Principal = Depends(require_role("BUYER"))) -> BuyerScope:
    from backend.app.services.buyer_links import assert_active

    assert_active(db, p)
    return BuyerScope(db, p)
