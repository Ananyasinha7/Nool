from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.auth.lockout import minutes_locked, register_failure, reset
from backend.app.auth.passwords import verify_password
from backend.app.auth.tokens import Principal
from backend.app.db import get_db
from backend.app.deps import current_principal
from backend.app.errors import AppError
from backend.app.models import Buyer, Unit, User
from backend.app.routers._cookies import clear_session, set_session
from backend.app.schemas.auth import LoginRequest, MeOut, MePatch, OkOut

router = APIRouter(tags=["auth"])
GENERIC = "Username or password is incorrect."  # never says which field was wrong (FR-01)


@router.post("/auth/login", response_model=MeOut)
def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)) -> MeOut:
    user = db.scalar(select(User).where(User.username == body.username.strip().lower()))
    if user is not None:
        wait = minutes_locked(user)
        if wait:
            raise AppError(429, f"Too many attempts. Try again in {wait} minutes.")
    if not verify_password(body.password, user.password_hash if user else None) or user is None:
        if user is not None:
            register_failure(user)
            db.commit()
        raise AppError(401, GENERIC)
    reset(user)
    db.commit()
    set_session(response, Principal(role=user.role, user_id=user.id, unit_id=user.unit_id))
    return _me(db, user)


@router.post("/auth/logout", response_model=OkOut)
def logout(response: Response) -> OkOut:
    clear_session(response)
    return OkOut()


def _me(db: Session, user: User) -> MeOut:
    unit = db.get(Unit, user.unit_id) if user.unit_id else None
    return MeOut(role=user.role, display_name=user.display_name, lang=user.lang if user.lang in ("en", "ta") else "en",
                 unit_id=user.unit_id, unit_name=unit.name if unit else None)


@router.get("/me", response_model=MeOut)
def me(p: Principal = Depends(current_principal), db: Session = Depends(get_db)) -> MeOut:
    if p.role == "BUYER":
        from backend.app.services.buyer_links import assert_active

        assert_active(db, p)
        buyer = db.get(Buyer, p.buyer_id)
        if buyer is None:
            raise AppError(401, "Please sign in.")
        return MeOut(role="BUYER", display_name=buyer.name, lang="en", buyer_name=buyer.name)
    user = db.get(User, p.user_id)
    if user is None:
        raise AppError(401, "Please sign in.")
    return _me(db, user)


@router.patch("/me", response_model=MeOut)
def patch_me(body: MePatch, p: Principal = Depends(current_principal), db: Session = Depends(get_db)) -> MeOut:
    if p.role == "BUYER":
        raise AppError(403, "Buyer language is fixed.")  # buyer Tamil is cut (Doc2 section 8)
    user = db.get(User, p.user_id)
    if user is None:
        raise AppError(401, "Please sign in.")
    user.lang = body.lang
    db.commit()
    return _me(db, user)
