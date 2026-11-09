from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select

from backend.app.models import Buyer, OutboxMessage
from backend.app.schemas.misc import OutboxOut
from backend.app.services.scope import MerchScope, merch_scope

router = APIRouter(tags=["outbox"])


@router.get("/outbox", response_model=list[OutboxOut])
def outbox(scope: MerchScope = Depends(merch_scope)) -> list[OutboxOut]:
    rows = scope.session.execute(select(OutboxMessage, Buyer.name).join(Buyer, Buyer.id == OutboxMessage.buyer_id)
                                 .order_by(OutboxMessage.created_at.desc())).all()
    return [OutboxOut(id=m.id, to=name, subject=m.subject, body=m.body, created_at=m.created_at) for m, name in rows]
