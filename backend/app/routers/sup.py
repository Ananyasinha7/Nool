from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.schemas.common import SupOrderCard
from backend.app.services import sup as svc
from backend.app.services.scope import SupervisorScope, sup_scope

router = APIRouter(tags=["supervisor"])


@router.get("/sup/orders", response_model=list[SupOrderCard])
def sup_orders(scope: SupervisorScope = Depends(sup_scope)) -> list[SupOrderCard]:
    return svc.cards(scope)
