"""Classifier behaviour with the network monkeypatched (no real Groq calls)."""
import json

import httpx
import pytest

from backend.app.ai import classify as C
from backend.app.ai import groq_client
from backend.app.config import get_settings
from backend.app.models import AiCache

TA = "2 தையல் மெசின் பழுது"


def _ok(cat="MACHINE_BREAKDOWN", conf=0.9, tr="2 machines broken"):
    return json.dumps({"translation_en": tr, "category": cat, "confidence": conf, "evidence": "x"})


@pytest.fixture()
def live(monkeypatch):
    s = get_settings()
    monkeypatch.setattr(s, "ai_mode", "live")
    monkeypatch.setattr(s, "groq_api_key", "test-key-not-real")
    monkeypatch.setattr(s, "groq_classify_model", "m1")
    monkeypatch.setattr(s, "groq_classify_fallbacks", "m2,m3")


def test_happy_path_and_cache_written(db, live, monkeypatch):
    monkeypatch.setattr(groq_client, "chat_json", lambda *a, **k: _ok())
    o = C.classify(db, TA)
    assert (o.category, o.source, o.model) == ("MACHINE_BREAKDOWN", "AI", "m1")
    assert db.get(AiCache, C.text_hash(TA)) is not None


def test_invalid_json_goes_to_next_model(db, live, monkeypatch):
    calls = []

    def fake(model, *a, **k):
        calls.append(model)
        return "not json at all" if model == "m1" else _ok()

    monkeypatch.setattr(groq_client, "chat_json", fake)
    assert C.classify(db, TA).model == "m2" and calls == ["m1", "m2"]


def test_unknown_category_rejected(db, live, monkeypatch):
    monkeypatch.setattr(groq_client, "chat_json", lambda m, *a, **k: _ok(cat="DROP_TABLE") if m != "m3" else _ok())
    assert C.classify(db, TA).model == "m3"


def test_low_confidence_becomes_needs_review(db, live, monkeypatch):
    monkeypatch.setattr(groq_client, "chat_json", lambda *a, **k: _ok(conf=0.5))
    o = C.classify(db, TA)
    assert o.category == "NEEDS_REVIEW" and o.source == "AI"


def test_429_moves_to_next_model(db, live, monkeypatch):
    def fake_post(url, **kw):
        model = kw["json"]["model"]
        if model == "m1":
            return httpx.Response(429, request=httpx.Request("POST", url))
        body = {"choices": [{"message": {"content": _ok()}}]}
        return httpx.Response(200, json=body, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", fake_post)
    assert C.classify(db, TA).model == "m2"


def test_all_models_fail_falls_back_to_rules(db, live, monkeypatch):
    def boom(*a, **k):
        raise groq_client.GroqError("down")

    monkeypatch.setattr(groq_client, "chat_json", boom)
    o = C.classify(db, TA)
    assert o.source == "RULE" and o.category == "MACHINE_BREAKDOWN" and o.confidence <= 0.6


def test_network_error_falls_back_to_rules(db, live, monkeypatch):
    def fail(*a, **k):
        raise httpx.ConnectError("offline")

    monkeypatch.setattr(httpx, "post", fail)
    assert C.classify(db, "இன்று மின்சாரம் இல்லை").source == "RULE"


def test_cache_hit_makes_no_network_call(db, live, monkeypatch):
    monkeypatch.setattr(groq_client, "chat_json", lambda *a, **k: _ok())
    C.classify(db, TA)

    def forbidden(*a, **k):
        raise AssertionError("network used despite cache")

    monkeypatch.setattr(groq_client, "chat_json", forbidden)
    assert C.classify(db, TA).category == "MACHINE_BREAKDOWN"


def test_rule_results_never_exceed_point_six():
    from backend.app.ai.rules import classify_rules

    assert classify_rules("மெசின் பழுது ரிப்பேர் இயந்திரம்").confidence <= 0.6


def test_no_key_uses_rules(db, monkeypatch):
    s = get_settings()
    monkeypatch.setattr(s, "ai_mode", "live")
    monkeypatch.setattr(s, "groq_api_key", "")
    assert C.classify(db, "15 ஆட்கள் வரவில்லை").source == "RULE"


def test_mock_mode_returns_golden_answer(db, monkeypatch):
    monkeypatch.setattr(get_settings(), "ai_mode", "mock")
    o = C.classify(db, "நீல நிற துணி வரவில்லை")
    assert o.category == "MATERIAL_SHORTAGE" and o.translation_en


def test_rule_ties_and_unknown_need_review():
    from backend.app.ai.rules import classify_rules

    assert classify_rules("hello there").category == "NEEDS_REVIEW"
    assert classify_rules("power cut and machine stop").category == "NEEDS_REVIEW"


def test_subcontractor_needs_both_parts():
    from backend.app.ai.rules import classify_rules

    assert classify_rules("பிரிண்டிங் தாமதம்").category == "SUBCONTRACTOR_DELAY"
    assert classify_rules("பிரிண்டிங்").category == "NEEDS_REVIEW"


def test_rate_limit_falls_back_to_rules(db, live, monkeypatch):
    monkeypatch.setattr(groq_client, "chat_json", lambda *a, **k: _ok())
    for i in range(C.AI_CALLS_PER_HOUR):
        C.classify(db, f"note number {i} machine", user_id="u-rate")
    assert C.classify(db, "a brand new machine note", user_id="u-rate").source == "RULE"
