from backend.tests.conftest import login


def test_login_ok_and_me(client):
    r = login(client, "priya.merch", "Nool@Demo2026")
    assert r.status_code == 200
    assert r.json()["role"] == "MERCHANDISER" and r.json()["displayName"] == "Priya"
    assert "httponly" in r.headers["set-cookie"].lower()
    assert client.get("/api/me").json()["lang"] == "en"


def test_supervisor_gets_tamil_default_and_unit(client):
    body = login(client, "murugan.u1", "246810").json()
    assert body["lang"] == "ta" and body["unitName"] == "Unit 1"


def test_wrong_credentials_generic_message(client):
    a = login(client, "priya.merch", "wrong")
    b = login(client, "nobody", "wrong")
    assert a.status_code == b.status_code == 401
    assert a.json()["error"]["message"] == b.json()["error"]["message"]
    assert a.json()["error"]["code"] == "UNAUTHENTICATED"


def test_lockout_after_five_bad_attempts(client):
    for _ in range(5):
        login(client, "selvi.u2", "bad")
    r = login(client, "selvi.u2", "246810")  # even the right PIN is refused while locked
    assert r.status_code == 429 and "minutes" in r.json()["error"]["message"]


def test_me_requires_sign_in(client):
    r = client.get("/api/me")
    assert r.status_code == 401 and r.json()["error"]["code"] == "UNAUTHENTICATED"


def test_patch_lang_and_logout(as_priya):
    assert as_priya.patch("/api/me", json={"lang": "ta"}).json()["lang"] == "ta"
    as_priya.post("/api/auth/logout")
    assert as_priya.get("/api/me").status_code == 401


def test_extra_fields_rejected(client):
    r = client.post("/api/auth/login", json={"username": "a", "password": "b", "admin": True})
    assert r.status_code == 422 and r.json()["error"]["code"] == "VALIDATION"


def test_cross_site_origin_blocked(as_priya):
    r = as_priya.patch("/api/me", json={"lang": "en"}, headers={"Origin": "https://evil.example"})
    assert r.status_code == 403
