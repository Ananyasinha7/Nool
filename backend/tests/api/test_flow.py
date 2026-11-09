"""The e2e story at API level (the browser version is frontend/e2e/offline-to-buyer.spec.ts):
supervisor logs a slow day -> board non-green -> draft warning -> merchandiser confirms -> buyer sees notice."""
import uuid

from sqlalchemy import select

from backend.app.models import Order
from backend.tests.conftest import buyer_client, login


def test_supervisor_to_buyer_story(client, db):
    po = "B-PO-88329"  # GREEN at seed
    oid = db.scalar(select(Order.id).where(Order.po_no == po))

    # 1. the supervisor on Unit 1 sends a very slow day, with a Tamil note
    login(client, "murugan.u1", "246810")
    log_id = str(uuid.uuid4())
    r = client.post("/api/logs", json={
        "id": log_id, "orderId": oid, "stageKey": "STITCHING", "logDate": "2026-11-03", "qty": 5,
        "noteText": "2 தையல் மெசின் பழுது", "clientCreatedAt": "2026-11-03T06:00:00Z"})
    assert r.status_code == 201

    # 2. the board now flags it (not green) with the maths, and a draft warning waits
    client.cookies.clear()
    login(client, "priya.merch", "Nool@Demo2026")
    row = next(o for o in client.get("/api/orders").json() if o["poNo"] == po)
    assert row["health"]["health"] in ("AMBER", "RED") and row["openWarning"] is True
    draft = next(w for w in client.get("/api/warnings").json() if w["poNo"] == po)
    assert draft["note"]["originalText"] == "2 தையல் மெசின் பழுது"
    assert draft["note"]["category"] == "MACHINE_BREAKDOWN"

    # 3. the buyer sees nothing until the merchandiser confirms
    client.cookies.clear()
    buyer_client(client, "demo-b-0001")
    assert next(o for o in client.get("/api/buyer/orders").json() if o["poNo"] == po)["delayNotice"] is None

    # 4. confirm -> the buyer now sees the notice (label and date impact, not the raw note)
    client.cookies.clear()
    login(client, "priya.merch", "Nool@Demo2026")
    done = client.post(f"/api/warnings/{draft['id']}/confirm", json={"category": "MACHINE_BREAKDOWN"})
    assert done.status_code == 200
    client.cookies.clear()
    buyer_client(client, "demo-b-0001")
    notice = next(o for o in client.get("/api/buyer/orders").json() if o["poNo"] == po)["delayNotice"]
    assert notice["categoryLabel"] == "Machine breakdown"
    assert "மெசின்" not in notice["text"]
