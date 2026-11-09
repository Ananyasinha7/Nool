"""Gate G3: every negative case in Doc3 section 14. A buyer must never see another buyer's data,
unconfirmed warnings, internal notes, units or supervisor names."""
import io
import json

from openpyxl import load_workbook
from sqlalchemy import select

from backend.app.models import Buyer, DailyLog, Order, Photo
from backend.tests.conftest import buyer_client, login


def _order(db, po):
    return db.scalar(select(Order).where(Order.po_no == po))


def _as_buyer(client, token):
    client.cookies.clear()
    return buyer_client(client, token)


def test_buyer_lists_only_own_orders(client):
    rows = _as_buyer(client, "demo-b-0001").get("/api/buyer/orders").json()
    assert rows and all(r["poNo"].startswith("B-") for r in rows)
    rows_c = _as_buyer(client, "demo-c-0001").get("/api/buyer/orders").json()
    assert rows_c and all(r["poNo"].startswith("C-") for r in rows_c)


def test_foreign_order_id_is_404(client, db):
    c = _as_buyer(client, "demo-b-0001")
    assert c.get(f"/api/buyer/orders/{_order(db, 'C-PO-0488').id}").status_code == 404
    assert c.get(f"/api/buyer/orders/{_order(db, 'D-PO-7710').id}").status_code == 404
    assert c.get("/api/buyer/orders/made-up-id").status_code == 404


def test_foreign_and_unshared_photos_are_404(client, db):
    own_unshared = db.scalar(select(Photo).join(DailyLog, DailyLog.id == Photo.log_id)
                             .join(Order, Order.id == DailyLog.order_id)
                             .where(Order.po_no.like("B-%"), Photo.share_with_buyer.is_(False)))
    own_shared = db.scalar(select(Photo).join(DailyLog, DailyLog.id == Photo.log_id)
                           .join(Order, Order.id == DailyLog.order_id)
                           .where(Order.po_no.like("B-%"), Photo.share_with_buyer.is_(True)))
    foreign_shared = db.scalar(select(Photo).join(DailyLog, DailyLog.id == Photo.log_id)
                               .join(Order, Order.id == DailyLog.order_id)
                               .where(Order.po_no.like("C-%"), Photo.share_with_buyer.is_(True)))
    c = _as_buyer(client, "demo-b-0001")
    assert c.get(f"/api/photos/{own_shared.id}").status_code == 200
    assert c.get(f"/api/photos/{own_unshared.id}").status_code == 404  # internal by default (D-08)
    assert c.get(f"/api/photos/{foreign_shared.id}").status_code == 404


def test_buyer_detail_lists_only_shared_photos(client, db):
    d = _as_buyer(client, "demo-b-0001").get(f"/api/buyer/orders/{_order(db, 'B-PO-88213').id}").json()
    assert len(d["photos"]) == 2 and all(p["url"].startswith("/api/photos/") for p in d["photos"])


def test_unconfirmed_warning_never_visible(client, db):
    c = _as_buyer(client, "demo-b-0001")
    rows = {r["poNo"]: r for r in c.get("/api/buyer/orders").json()}
    assert rows["B-PO-88240"]["delayNotice"] is None  # only a DRAFT exists
    assert rows["B-PO-88301"]["delayNotice"] is None
    assert rows["B-PO-88213"]["delayNotice"]["categoryLabel"] == "Machine breakdown"  # confirmed


def test_payloads_leak_no_internal_data(client, db):
    c = _as_buyer(client, "demo-b-0001")
    blobs = [c.get("/api/buyer/orders").text]
    for o in c.get("/api/buyer/orders").json():
        blobs.append(c.get(f"/api/buyer/orders/{o['id']}").text)
    text = " ".join(blobs)
    for secret in ("Unit 1", "Unit 2", "Unit 3", "Print House", "Murugan", "Selvi", "Kumar", "murugan.u1",
                   "machine problem", "மெசின்", "மின்சாரம்", "confidence", "snapshot", "health", "ratio",
                   "actualPerDay", "requiredPerDay", "Company C", "Company D"):
        assert secret not in text, secret


def test_buyer_response_keys_are_the_allow_list(client):
    row = _as_buyer(client, "demo-b-0001").get("/api/buyer/orders").json()[0]
    assert set(row) == {"id", "poNo", "style", "colour", "qty", "exFactory", "progressPct", "currentStage",
                        "delayNotice"}


def test_date_history_shows_merchandiser_name_not_id(client, db):
    d = _as_buyer(client, "demo-b-0001").get(f"/api/buyer/orders/{_order(db, 'B-PO-88213').id}").json()
    assert [h["changedBy"] for h in d["dateHistory"]] == ["Priya", "Priya"]
    assert d["dateHistory"][0]["fromDate"] == "2026-11-11"


def test_buyer_cannot_reach_staff_routes(client):
    c = _as_buyer(client, "demo-b-0001")
    for path in ("/api/orders", "/api/warnings", "/api/outbox", "/api/lookups", "/api/sup/orders"):
        assert c.get(path).status_code == 403, path
    assert c.post("/api/logs", json={}).status_code == 403


def test_staff_cannot_use_buyer_routes(client):
    login(client, "priya.merch", "Nool@Demo2026")
    assert client.get("/api/buyer/orders").status_code == 403


def test_export_scoped_to_buyer(client, db):
    c = _as_buyer(client, "demo-b-0001")
    other = db.scalar(select(Buyer.id).where(Buyer.name == "Company C"))
    assert c.get(f"/api/export/weekly?buyerId={other}").status_code == 404
    wb = load_workbook(io.BytesIO(c.get("/api/export/weekly").content))
    assert wb.sheetnames == ["Company B"]
    statuses = {row[7].value for row in wb["Company B"].iter_rows(min_row=2)}
    assert statuses <= {"Delay notice", "In progress"}  # no Late/Watch colours for buyers


def test_merch_export_has_all_buyers_and_status(as_priya):
    wb = load_workbook(io.BytesIO(as_priya.get("/api/export/weekly").content))
    assert wb.sheetnames == ["Company B", "Company C", "Company D"]
    assert {r[7].value for r in wb["Company B"].iter_rows(min_row=2)} >= {"Late", "Watch"}
    one = load_workbook(io.BytesIO(as_priya.get("/api/export/weekly?week=2026-W47").content))
    assert all(r[0].value for r in one["Company B"].iter_rows(min_row=2))


def test_invalid_token_calm_401(client):
    r = client.post("/api/buyer/session", json={"token": "totally-wrong-token"})
    assert r.status_code == 401 and "no longer active" in r.json()["error"]["message"]


def test_revoked_link_stops_working_immediately(client, db):
    login(client, "priya.merch", "Nool@Demo2026")
    buyer_id = db.scalar(select(Buyer.id).where(Buyer.name == "Company B"))
    made = client.post(f"/api/buyers/{buyer_id}/links", json={"label": "test"}).json()
    token = made["url"].rsplit("/", 1)[1]
    c = _as_buyer(client, token)
    assert c.get("/api/buyer/orders").status_code == 200
    # revoke while the buyer's session is still open
    login(client, "priya.merch", "Nool@Demo2026")
    assert client.delete(f"/api/buyer-links/{made['id']}").status_code == 200
    client.cookies.clear()
    client.post("/api/buyer/session", json={"token": token})  # cannot start a new session
    client.cookies.clear()
    assert client.post("/api/buyer/session", json={"token": token}).status_code == 401


def test_open_buyer_session_dies_when_link_revoked(client, db):
    login(client, "priya.merch", "Nool@Demo2026")
    buyer_id = db.scalar(select(Buyer.id).where(Buyer.name == "Company B"))
    made = client.post(f"/api/buyers/{buyer_id}/links", json={}).json()
    token = made["url"].rsplit("/", 1)[1]
    client.cookies.clear()
    assert client.post("/api/buyer/session", json={"token": token}).status_code == 200
    buyer_cookie = client.cookies.get("nool_session")
    assert client.get("/api/buyer/orders").status_code == 200
    from datetime import UTC, datetime

    from backend.app.models import BuyerLink

    db.get(BuyerLink, made["id"]).revoked_at = datetime.now(UTC)
    db.flush()
    client.cookies.set("nool_session", buyer_cookie)
    assert client.get("/api/buyer/orders").status_code == 401  # same cookie, link now revoked


def test_link_token_only_stored_as_hash(client, db):
    from backend.app.models import BuyerLink

    login(client, "priya.merch", "Nool@Demo2026")
    buyer_id = db.scalar(select(Buyer.id).where(Buyer.name == "Company B"))
    token = client.post(f"/api/buyers/{buyer_id}/links", json={}).json()["url"].rsplit("/", 1)[1]
    for link in db.scalars(select(BuyerLink)):
        assert token not in json.dumps({"h": link.token_hash, "l": link.label})
        assert link.token_hash != token and len(link.token_hash) == 64


def test_buyer_has_no_tamper_path_via_cookie(client):
    _as_buyer(client, "demo-b-0001")
    client.cookies.set("nool_session", "forged.token.value")
    assert client.get("/api/buyer/orders").status_code == 401
