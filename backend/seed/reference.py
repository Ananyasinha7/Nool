"""Reference data: units, demo users, buyers, buyer links, TNA template, holidays (Doc3 section 13).

All credentials here are synthetic DEMO values documented in deployment.md. Real
deployments must change them; real buyer links use random tokens (F-5).
"""
from __future__ import annotations

import hashlib
from datetime import date

import bcrypt
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import get_tna
from backend.app.models import Buyer, BuyerLink, Holiday, TnaItem, TnaTemplate, Unit, User

UNITS = [("Unit 1", "OWN"), ("Unit 2", "OWN"), ("Unit 3", "OWN"),
         ("Print House", "SUBCONTRACT"), ("Wash House", "SUBCONTRACT")]

MERCH_PASSWORD = "Nool@Demo2026"  # demo-only
SUP_PIN = "246810"  # demo-only

USERS = [  # username, display, role, unit, lang, secret
    ("priya.merch", "Priya", "MERCHANDISER", None, "en", MERCH_PASSWORD),
    ("murugan.u1", "Murugan", "SUPERVISOR", "Unit 1", "ta", SUP_PIN),
    ("selvi.u2", "Selvi", "SUPERVISOR", "Unit 2", "ta", SUP_PIN),
    ("kumar.print", "Kumar", "SUPERVISOR", "Print House", "ta", SUP_PIN),
    ("anbu.u3", "Anbu", "SUPERVISOR", "Unit 3", "ta", SUP_PIN),
]

BUYERS = [("Company B", "UK"), ("Company C", "Germany"), ("Company D", "Netherlands")]
DEMO_TOKENS = {"Company B": "demo-b-0001", "Company C": "demo-c-0001", "Company D": "demo-d-0001"}

# Placeholder holiday dates (A-01): clearly labelled, outside the demo window that matters.
HOLIDAYS = [(date(2026, 12, 25), "Christmas (placeholder)"), (date(2027, 1, 1), "New Year (placeholder)"),
            (date(2027, 1, 14), "Pongal (placeholder)")]


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _hash_pw(secret: str) -> str:
    return bcrypt.hashpw(secret.encode(), bcrypt.gensalt(rounds=10)).decode()


def seed_reference(s: Session) -> dict[str, dict]:
    ids: dict[str, dict] = {"units": {}, "users": {}, "buyers": {}, "template": {}}
    for name, kind in UNITS:
        row = s.scalar(select(Unit).where(Unit.name == name)) or Unit(name=name, kind=kind)
        s.add(row)
        s.flush()
        ids["units"][name] = row.id

    for username, display, role, unit, lang, secret in USERS:
        row = s.scalar(select(User).where(User.username == username))
        if row is None:
            row = User(username=username, display_name=display, role=role, lang=lang,
                       unit_id=ids["units"][unit] if unit else None, password_hash=_hash_pw(secret))
            s.add(row)
            s.flush()
        ids["users"][username] = row.id

    for name, country in BUYERS:
        row = s.scalar(select(Buyer).where(Buyer.name == name)) or Buyer(name=name, country=country)
        s.add(row)
        s.flush()
        ids["buyers"][name] = row.id
        th = hash_token(DEMO_TOKENS[name])
        if s.scalar(select(BuyerLink).where(BuyerLink.token_hash == th)) is None:
            s.add(BuyerLink(buyer_id=row.id, token_hash=th, label="Demo link"))

    tpl = s.scalar(select(TnaTemplate).where(TnaTemplate.name == "Standard"))
    if tpl is None:
        tpl = TnaTemplate(name="Standard")
        s.add(tpl)
        s.flush()
        for i, it in enumerate(get_tna()):
            s.add(TnaItem(template_id=tpl.id, name=it["name"], kind=it["kind"], stage_key=it.get("stageKey"),
                          offset_days=it["offsetDays"], print_only=it.get("printOnly", False), sort_order=i))
    ids["template"]["Standard"] = tpl.id

    for d, name in HOLIDAYS:
        if s.get(Holiday, d) is None:
            s.add(Holiday(date=d, name=name))
    s.flush()
    return ids
