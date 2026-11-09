"""Magic links (F-5, D-09): random token, only its SHA-256 is stored, revocable."""
from __future__ import annotations

import hashlib
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import get_settings
from backend.app.models import BuyerLink


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_link(session: Session, buyer_id: str, label: str) -> tuple[BuyerLink, str]:
    token = secrets.token_urlsafe(32)
    link = BuyerLink(buyer_id=buyer_id, token_hash=hash_token(token), label=label)
    session.add(link)
    session.flush()
    return link, f"{get_settings().app_url.rstrip('/')}/b/{token}"


def resolve(session: Session, token: str) -> BuyerLink | None:
    link = session.scalar(select(BuyerLink).where(BuyerLink.token_hash == hash_token(token)))
    return link if link is not None and link.revoked_at is None else None


INVALID = "This link is no longer active. Please contact your merchandiser."


def assert_active(session: Session, principal) -> None:
    """A buyer cookie is only as good as its link: a revoked (or deleted) link ends the session at once."""
    from backend.app.errors import AppError

    link = session.get(BuyerLink, principal.link_id) if principal.link_id else None
    if link is None or link.revoked_at is not None or link.buyer_id != principal.buyer_id:
        raise AppError(401, INVALID)
