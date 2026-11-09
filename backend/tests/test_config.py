import json
from datetime import date

from backend.app.clock import get_today
from backend.app.config import CONTRACT_DIR, get_config, get_settings, get_tna


def test_config_matches_the_shared_contract_file():
    raw = json.loads((CONTRACT_DIR / "config.json").read_text(encoding="utf-8"))
    cfg = get_config()
    assert cfg.work_days == (1, 2, 3, 4, 5, 6)  # Mon-Sat, ISO weekdays (A-01)
    assert cfg.rate_weights == (3, 2, 1)
    assert (cfg.ratio_green, cfg.ratio_amber) == (1.0, 0.8)
    assert (cfg.slip_amber_min, cfg.slip_red_min) == (1, 3)
    assert cfg.qty_cap == raw["qtyCap"] == 1.05 and cfg.backdate_days == 3
    assert cfg.ai_confidence_min == 0.7 and cfg.session_days["SUPERVISOR"] == 30


def test_tna_template_offsets():
    tna = get_tna()
    assert [i["offsetDays"] for i in tna] == [40, 32, 24, 16, 7, 3, 2, 1]
    assert next(i for i in tna if i["name"] == "Printing complete")["printOnly"] is True
    assert {i["kind"] for i in tna} == {"STAGE", "MANUAL"}


def test_demo_clock_is_honoured(monkeypatch):
    s = get_settings()
    monkeypatch.setattr(s, "demo_today", "2026-11-03")
    assert get_today() == date(2026, 11, 3)
    monkeypatch.setattr(s, "demo_today", "")
    assert get_today() == date.today()
