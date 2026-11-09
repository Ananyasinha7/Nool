"""Weekly status workbook, one sheet per buyer (A-14, D-14)."""
from __future__ import annotations

import io

from openpyxl import Workbook
from openpyxl.styles import Font
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.clock import get_today
from backend.app.models import Buyer, Order, Warning
from backend.app.services.health import health_for
from backend.app.services.orders import iso_week

HEAD = ["PO", "Style", "Colour", "Qty", "Done (current stage)", "Stage", "Ex-factory", "Status", "Last update"]
STATUS = {"GREEN": "On track", "AMBER": "Watch", "RED": "Late", "GREY": "No recent update"}


def build_workbook(session: Session, buyer_ids: list[str], week: str | None, internal: bool) -> bytes:
    """internal=False is the buyer's copy: no health colours, only a delay notice when a merchandiser
    has confirmed one (BR-05)."""
    wb = Workbook()
    wb.remove(wb.active)
    for buyer in session.scalars(select(Buyer).where(Buyer.id.in_(buyer_ids)).order_by(Buyer.name)):
        ws = wb.create_sheet(title=buyer.name[:31])
        ws.append(HEAD)
        for c in ws[1]:
            c.font = Font(bold=True)
        orders = [o for o in session.scalars(select(Order).where(Order.buyer_id == buyer.id).order_by(Order.ex_factory))
                  if week is None or iso_week(o.ex_factory) == week]
        health = health_for(session, orders, get_today())
        confirmed = set(session.scalars(select(Warning.order_id).where(
            Warning.order_id.in_([o.id for o in orders]), Warning.status == "CONFIRMED")))
        for o in orders:
            h = health[o.id]
            status = STATUS[h.health] if internal else ("Delay notice" if o.id in confirmed else "In progress")
            ws.append([o.po_no, o.style, o.colour, o.qty, h.done, h.active_stage or "COMPLETE", o.ex_factory,
                       status, h.last_log_date])
        ws.freeze_panes = "A2"
        for col, width in zip("ABCDEFGHI", (14, 28, 12, 9, 20, 12, 12, 16, 12), strict=True):
            ws.column_dimensions[col].width = width
    if not wb.sheetnames:
        wb.create_sheet("No data")
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
