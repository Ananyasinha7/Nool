from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select

from backend.app.errors import AppError
from backend.app.models import Buyer, BuyerLink
from backend.app.schemas.auth import OkOut
from backend.app.schemas.misc import LinkCreated, LinkLabel, LinkOut
from backend.app.services import buyer_links as svc
from backend.app.services.audit import audit
from backend.app.services.scope import MerchScope, merch_scope

router = APIRouter(tags=["buyer-links"])


@router.post("/buyers/{buyer_id}/links", response_model=LinkCreated, status_code=201)
def create_link(buyer_id: str, body: LinkLabel | None = None, scope: MerchScope = Depends(merch_scope)) -> LinkCreated:
    if scope.session.get(Buyer, buyer_id) is None:
        raise AppError(404, "Buyer not found.")
    link, url = svc.create_link(scope.session, buyer_id, (body.label if body else "") or "Link")
    audit(scope.session, scope.principal.user_id, "BUYER_LINK_CREATED", "buyer_link", link.id)
    scope.session.commit()
    return LinkCreated(id=link.id, url=url)  # the token is never stored or logged


@router.get("/buyers/{buyer_id}/links", response_model=list[LinkOut])
def list_links(buyer_id: str, scope: MerchScope = Depends(merch_scope)) -> list[LinkOut]:
    rows = scope.session.scalars(select(BuyerLink).where(BuyerLink.buyer_id == buyer_id)
                                 .order_by(BuyerLink.created_at.desc()))
    return [LinkOut(id=r.id, label=r.label, created_at=r.created_at, revoked=r.revoked_at is not None) for r in rows]


@router.delete("/buyer-links/{link_id}", response_model=OkOut)
def revoke(link_id: str, scope: MerchScope = Depends(merch_scope)) -> OkOut:
    link = scope.session.get(BuyerLink, link_id)
    if link is None:
        raise AppError(404, "Link not found.")
    link.revoked_at = datetime.now(UTC)  # takes effect immediately: resolve() checks it on every session start
    audit(scope.session, scope.principal.user_id, "BUYER_LINK_REVOKED", "buyer_link", link.id)
    scope.session.commit()
    return OkOut()
