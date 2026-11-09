"""Regenerates contract/fixtures/*.json from the real API against a SEEDED DEVELOPMENT database.
Needs DATABASE_URL and DEMO_TODAY=2026-11-03:  python scripts/export_fixtures.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from backend.app.main import app  # noqa: E402

OUT = ROOT / "contract" / "fixtures"


def dump(name: str, data: object) -> None:
    (OUT / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with TestClient(app) as c:
        c.post("/api/auth/login", json={"username": "priya.merch", "password": "Nool@Demo2026"})
        orders = c.get("/api/orders").json()
        dump("orders", orders)
        sample = next(o for o in orders if o["poNo"] == "B-PO-88240")
        dump("orderHealth", sample["health"])
        dump("warnings", c.get("/api/warnings").json())
        c.cookies.clear()
        c.post("/api/auth/login", json={"username": "murugan.u1", "password": "246810"})
        dump("supCards", c.get("/api/sup/orders").json())
        c.cookies.clear()
        c.post("/api/buyer/session", json={"token": "demo-b-0001"})
        first = c.get("/api/buyer/orders").json()
        confirmed = next(o for o in first if o["delayNotice"])
        dump("buyerOrder", c.get(f"/api/buyer/orders/{confirmed['id']}").json())
    print("wrote fixtures")


if __name__ == "__main__":
    main()
