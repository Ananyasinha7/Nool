"""Every seeded order lands on its target status (G2), and the samples have exact done quantities."""
from datetime import date

from sqlalchemy import select

from backend.app.models import Order
from backend.app.services.health import health_for
from backend.seed.orders import ORDERS

TODAY = date(2026, 11, 3)
TARGET = {o[0]: o[9] for o in ORDERS}


def _all(db):
    orders = db.scalars(select(Order)).all()
    return {o.po_no: h for o, h in ((o, health_for(db, [o], TODAY)[o.id]) for o in orders)}


def test_every_order_matches_target(db):
    got = _all(db)
    assert set(got) == set(TARGET)
    assert {po: h.health for po, h in got.items()} == TARGET


def test_sample_done_quantities_exact(db):
    got = _all(db)
    assert got["B-PO-88213"].done == 6800
    assert got["B-PO-88240"].done == 5200
    assert got["C-PO-0488"].done == 3100


def test_board_counts_match_doc3(db):
    counts = {}
    for h in _all(db).values():
        counts[h.health] = counts.get(h.health, 0) + 1
    assert counts == {"RED": 2, "AMBER": 3, "GREEN": 7, "GREY": 1}


def test_several_non_green_flagged_14_days_early(db):
    early = [po for po, h in _all(db).items() if h.health in ("AMBER", "RED") and h.lead_days >= 14]
    assert len(early) >= 3  # A-15: KPI-1 demo proxy
