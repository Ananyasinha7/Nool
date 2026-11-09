from sqlalchemy import select

from backend.app.models import Buyer, Order, TnaTemplate, Unit


def _ids(db):
    return {
        "buyer": db.scalar(select(Buyer.id).where(Buyer.name == "Company B")),
        "unit": db.scalar(select(Unit.id).where(Unit.name == "Unit 1")),
        "tpl": db.scalar(select(TnaTemplate.id)),
    }


def _payload(db, **over):
    i = _ids(db)
    body = {"poNo": "T-PO-1", "buyerId": i["buyer"], "style": "Test tee", "colour": "red", "unitId": i["unit"],
            "hasPrint": False, "hasWash": False, "exFactory": "2026-12-30", "templateId": i["tpl"],
            "lines": [{"size": "M", "qty": 600}, {"size": "L", "qty": 400}]}
    body.update(over)
    return body


def test_board_sorted_by_severity_then_slip(as_priya):
    rows = as_priya.get("/api/orders").json()
    assert len(rows) == 13
    order = [r["health"]["health"] for r in rows]
    assert order[:2] == ["RED", "RED"] and order[2:5] == ["AMBER"] * 3 and order[-1] == "GREEN"
    assert rows[0]["poNo"] == "B-PO-88301"  # slip 9 days beats 4 days


def test_sample_maths_visible(as_priya):
    rows = {r["poNo"]: r for r in as_priya.get("/api/orders").json()}
    h = rows["B-PO-88240"]["health"]
    assert h["health"] == "RED" and h["workingDaysLeft"] == 6 and round(h["actualPerDay"]) == 299


def test_filters_combine(as_priya, db):
    b = _ids(db)["buyer"]
    rows = as_priya.get(f"/api/orders?buyerId={b}&status=RED").json()
    assert {r["poNo"] for r in rows} == {"B-PO-88240", "B-PO-88301"}
    assert [r["poNo"] for r in as_priya.get("/api/orders?q=0488").json()] == ["C-PO-0488"]
    wk = as_priya.get("/api/orders?shipWeek=2026-W47").json()
    assert all(r["exFactory"].startswith("2026-11-2") for r in wk) and wk


def test_lookups(as_priya):
    j = as_priya.get("/api/lookups").json()
    assert len(j["buyers"]) == 3 and j["shipWeeks"] == sorted(j["shipWeeks"])


def test_create_order_generates_milestones(as_priya, db):
    r = as_priya.post("/api/orders", json=_payload(db))
    assert r.status_code == 201
    d = as_priya.get(f"/api/orders/{r.json()['id']}").json()
    assert d["qty"] == 1000
    names = [m["name"] for m in d["milestones"]]
    assert "Printing complete" not in names  # printOnly skipped without print
    stitch = next(m for m in d["milestones"] if m["name"] == "Stitching complete")
    assert stitch["plannedDate"] == "2026-12-23"  # 7 calendar days before 30 Dec
    assert d["health"]["lowConfidence"] is True  # no logs yet: planned rate shown


def test_create_order_with_print_adds_printing(as_priya, db):
    r = as_priya.post("/api/orders", json=_payload(db, poNo="T-PO-2", hasPrint=True))
    d = as_priya.get(f"/api/orders/{r.json()['id']}").json()
    assert "Printing complete" in [m["name"] for m in d["milestones"]]
    assert {a["stageKey"] for a in d["assignments"]} >= {"PRINTING", "CUTTING"}


def test_duplicate_po_rejected(as_priya, db):
    assert as_priya.post("/api/orders", json=_payload(db, poNo="B-PO-88213")).status_code == 409


def test_qty_must_equal_line_sum(as_priya, db):
    r = as_priya.post("/api/orders", json=_payload(db, qty=999))
    assert r.status_code == 422 and "qty" in r.json()["error"]["fields"]


def test_supervisor_cannot_use_merch_routes(as_murugan):
    assert as_murugan.get("/api/orders").status_code == 403


def test_date_change_requires_reason_and_is_recorded(as_priya, db):
    oid = db.scalar(select(Order.id).where(Order.po_no == "C-PO-0488"))
    bad = as_priya.patch(f"/api/orders/{oid}/ex-factory", json={"toDate": "2026-12-05", "reasonCode": "OTHER"})
    assert bad.status_code == 422
    ok = as_priya.patch(f"/api/orders/{oid}/ex-factory",
                        json={"toDate": "2026-12-05", "reasonCode": "CAPACITY"})
    assert ok.status_code == 200 and ok.json()["exFactory"] == "2026-12-05"
    ch = as_priya.get(f"/api/orders/{oid}/changes").json()
    assert ch[-1]["fromDate"] == "2026-11-28" and ch[-1]["changedByName"] == "Priya"
    # milestones follow the new date: stitching complete = 7 days before 5 Dec
    stitch = next(m for m in ok.json()["milestones"] if m["name"] == "Stitching complete")
    assert stitch["plannedDate"] == "2026-11-28"
    assert ok.json()["exFactoryOriginal"] == "2026-11-28"


def test_same_date_rejected(as_priya, db):
    oid = db.scalar(select(Order.id).where(Order.po_no == "C-PO-0488"))
    r = as_priya.patch(f"/api/orders/{oid}/ex-factory", json={"toDate": "2026-11-28", "reasonCode": "CAPACITY"})
    assert r.status_code == 422


def test_manual_milestone_tick_only(as_priya, db):
    oid = db.scalar(select(Order.id).where(Order.po_no == "B-PO-88340"))
    d = as_priya.get(f"/api/orders/{oid}").json()
    manual = next(m for m in d["milestones"] if m["kind"] == "MANUAL" and m["actualDate"] is None)
    stage = next(m for m in d["milestones"] if m["kind"] == "STAGE")
    assert as_priya.patch(f"/api/milestones/{manual['id']}", json={"actualDate": "2026-11-03"}).status_code == 200
    assert as_priya.patch(f"/api/milestones/{stage['id']}", json={"actualDate": "2026-11-03"}).status_code == 409


def test_order_logs_and_changes_endpoints(as_priya, db):
    oid = db.scalar(select(Order.id).where(Order.po_no == "B-PO-88213"))
    logs = as_priya.get(f"/api/orders/{oid}/logs?days=10").json()
    assert logs and logs[0]["logDate"] == "2026-11-02" and logs[0]["qty"] == 490
    assert len(as_priya.get(f"/api/orders/{oid}/changes").json()) == 2


def test_unknown_order_404(as_priya):
    assert as_priya.get("/api/orders/nope").status_code == 404


def test_tna_templates(as_priya):
    t = as_priya.get("/api/tna-templates").json()
    assert t[0]["name"] == "Standard" and len(t[0]["items"]) == 8


def test_order_with_wash_gets_washing_stage_and_milestone(as_priya, db):
    i = _ids(db)
    wash_unit = db.scalar(select(Unit.id).where(Unit.name == "Wash House"))
    r = as_priya.post("/api/orders", json=_payload(db, poNo="T-PO-WASH", hasWash=True, washUnitId=wash_unit))
    assert r.status_code == 201
    d = as_priya.get(f"/api/orders/{r.json()['id']}").json()
    wash = next(m for m in d["milestones"] if m["name"] == "Washing complete")
    assert wash["stageKey"] == "WASHING" and wash["plannedDate"] == "2026-12-20"  # 10 calendar days before 30 Dec
    assignments = {a["stageKey"]: a["unitName"] for a in d["assignments"]}
    assert assignments["WASHING"] == "Wash House" and assignments["CUTTING"] == "Unit 1"
    assert d["health"]["health"] in ("GREEN", "AMBER", "RED", "GREY") and i  # projection copes with the extra stage
