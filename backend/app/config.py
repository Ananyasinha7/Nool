"""Settings (env) and the shared contract files (contract/config.json, tna.json).

The JSON files are shared with the frontend, so numbers like thresholds live in
one place only (Doc3 section 5.1).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_DIR = REPO_ROOT / "contract"


@dataclass(frozen=True)
class Config:
    work_days: tuple[int, ...]
    rate_weights: tuple[int, ...]
    ratio_green: float
    ratio_amber: float
    slip_amber_min: int
    slip_red_min: int
    stale_workdays: int
    early_lead_days: int
    stage_lag_wd: int
    inspection_wd: int
    qty_cap: float
    backdate_days: int
    ai_confidence_min: float
    session_days: dict[str, int]
    max_failed_logins: int
    lockout_min: int
    photo_max_bytes: int
    audio_max_seconds: int


def _load_json(name: str) -> Any:
    return json.loads((CONTRACT_DIR / name).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def get_config() -> Config:
    raw = _load_json("config.json")
    return Config(
        work_days=tuple(raw["workDays"]),
        rate_weights=tuple(raw["rateWeights"]),
        ratio_green=raw["ratioGreen"],
        ratio_amber=raw["ratioAmber"],
        slip_amber_min=raw["slipAmberMin"],
        slip_red_min=raw["slipRedMin"],
        stale_workdays=raw["staleWorkdays"],
        early_lead_days=raw["earlyLeadDays"],
        stage_lag_wd=raw["stageLagWd"],
        inspection_wd=raw["inspectionWd"],
        qty_cap=raw["qtyCap"],
        backdate_days=raw["backdateDays"],
        ai_confidence_min=raw["aiConfidenceMin"],
        session_days=dict(raw["sessionDays"]),
        max_failed_logins=raw["maxFailedLogins"],
        lockout_min=raw["lockoutMin"],
        photo_max_bytes=raw["photoMaxBytes"],
        audio_max_seconds=raw["audioMaxSeconds"],
    )


@lru_cache(maxsize=1)
def get_tna() -> list[dict[str, Any]]:
    return list(_load_json("tna.json"))


class Settings(BaseSettings):
    """Environment variables. Names only in .env.example; values stay local."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = ""
    direct_url: str = ""
    jwt_secret: str = "dev-only-change-me-dev-only-change-me"
    groq_api_key: str = ""
    groq_classify_model: str = "openai/gpt-oss-120b"
    groq_classify_fallbacks: str = "openai/gpt-oss-20b,qwen/qwen3.8-27b"
    groq_stt_model: str = "whisper-large-v3"
    ai_mode: str = "mock"  # "live" or "mock"
    demo_today: str = ""
    demo_logins_visible: bool = False
    app_url: str = "http://localhost:5173"
    env: str = "dev"  # "dev" or "prod"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
