from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.auth.tokens import Principal
from backend.app.db import get_db
from backend.app.deps import require_role
from backend.app.errors import AppError
from backend.app.export.weekly import build_workbook
from backend.app.models import Buyer

router = APIRouter(tags=["export"])
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/export/weekly")
def weekly(buyer_id: str | None = Query(None, alias="buyerId"),
           week: str | None = Query(None, pattern=r"^\d{4}-W\d{2}$"),
           p: Principal = Depends(require_role("MERCHANDISER", "BUYER")), db: Session = Depends(get_db)) -> Response:
    if p.role == "BUYER":
        from backend.app.services.buyer_links import assert_active

        assert_active(db, p)
        buyer_ids = [p.buyer_id]  # a buyer can only ever export their own company, whatever they ask for
        if buyer_id and buyer_id != p.buyer_id:
            raise AppError(404, "Buyer not found.")
    elif buyer_id:
        if db.get(Buyer, buyer_id) is None:
            raise AppError(404, "Buyer not found.")
        buyer_ids = [buyer_id]
    else:
        buyer_ids = list(db.scalars(select(Buyer.id)))
    data = build_workbook(db, buyer_ids, week, internal=p.role == "MERCHANDISER")
    name = f"nool-status-{week or 'all'}.xlsx"
    return Response(content=data, media_type=XLSX, headers={"Content-Disposition": f'attachment; filename="{name}"'})
