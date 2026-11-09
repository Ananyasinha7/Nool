import pytest
from sqlalchemy import select

from backend.app.auth.tokens import Principal
from backend.app.errors import AppError
from backend.app.models import Buyer, Order, Unit
from backend.app.services.scope import BuyerScope, MerchScope, SupervisorScope


def _id(db, po):
    return db.scalar(select(Order.id).where(Order.po_no == po))


def test_buyer_scope_only_own_orders(db):
    b = db.scalar(select(Buyer).where(Buyer.name == "Company B"))
    scope = BuyerScope(db, Principal(role="BUYER", buyer_id=b.id))
    orders = db.scalars(scope.order_query()).all()
    assert orders and all(o.buyer_id == b.id for o in orders)
    with pytest.raises(AppError) as e:
        scope.get_order(_id(db, "C-PO-0488"))
    assert e.value.status_code == 404


def test_supervisor_scope_other_unit_is_403(db):
    unit1 = db.scalar(select(Unit).where(Unit.name == "Unit 1"))
    scope = SupervisorScope(db, Principal(role="SUPERVISOR", user_id="u", unit_id=unit1.id))
    assert scope.get_order(_id(db, "B-PO-88213")).po_no == "B-PO-88213"
    with pytest.raises(AppError) as e:
        scope.get_order(_id(db, "B-PO-88240"))  # Unit 2's order
    assert e.value.status_code == 403


def test_merch_sees_everything(db):
    s = MerchScope(db, Principal(role="MERCHANDISER", user_id="p"))
    assert len(db.scalars(s.order_query()).all()) == 13
