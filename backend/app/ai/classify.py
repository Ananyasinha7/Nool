"""Tamil note -> English translation + category, with a deterministic fallback (Doc3 section 11, BR-07).

Order: cache -> primary model -> each fallback model -> keyword rules. Output is validated; low
confidence becomes NEEDS_REVIEW. AI latency never blocks the numbers: this runs after the log commits."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from sqlalchemy.orm import Session

from backend.app.ai import groq_client
from backend.app.ai.prompt import SYSTEM_PROMPT, user_message
from backend.app.ai.rules import classify_rules, normalise
from backend.app.config import get_config, get_settings
from backend.app.models import AiCache, RateLimit

AI_CALLS_PER_HOUR = 30
Category = Literal["MACHINE_BREAKDOWN", "POWER_CUT", "ABSENTEEISM", "MATERIAL_SHORTAGE", "QUALITY_REWORK",
                   "SUBCONTRACTOR_DELAY", "APPROVAL_PENDING", "OTHER"]
GOLDEN = Path(__file__).with_name("golden.json")


class ClassifyResult(BaseModel):
    """Strict schema for model output (anything else is rejected and the next model is tried)."""
    model_config = ConfigDict(extra="ignore")
    translation_en: str = Field(max_length=1000)
    category: Category
    confidence: float
    evidence: str = ""

    @field_validator("confidence")
    @classmethod
    def _clamp(cls, v: float) -> float:
        return min(1.0, max(0.0, v))


@dataclass(frozen=True)
class Outcome:
    translation_en: str
    category: str          # includes NEEDS_REVIEW
    confidence: float | None
    source: str            # AI | RULE
    model: str | None = None


def text_hash(text: str) -> str:
    return hashlib.sha256(normalise(text).encode()).hexdigest()


@lru_cache(maxsize=1)
def _golden() -> dict[str, dict]:
    return {normalise(g["text"]): g for g in json.loads(GOLDEN.read_text(encoding="utf-8"))}


def _apply_threshold(r: ClassifyResult, model: str) -> Outcome:
    category = r.category if r.confidence >= get_config().ai_confidence_min else "NEEDS_REVIEW"
    return Outcome(r.translation_en, category, r.confidence, "AI", model)


def _rate_limited(session: Session, user_id: str | None) -> bool:
    """30 AI calls per user per hour (rate_limits table). The rules path still works when limited."""
    if not user_id:
        return False
    key, now = f"ai:{user_id}", datetime.now(UTC)
    row = session.get(RateLimit, key)
    if row is None or now - row.window_start > timedelta(hours=1):
        session.merge(RateLimit(key=key, count=1, window_start=now))
        return False
    if row.count >= AI_CALLS_PER_HOUR:
        return True
    row.count += 1
    return False


def _rule_outcome(text: str) -> Outcome:
    r = classify_rules(text)
    return Outcome("", r.category, r.confidence, "RULE")


def classify(session: Session, text: str, user_id: str | None = None) -> Outcome:
    """Never raises: every failure path ends in the rules."""
    h = text_hash(text)
    cached = session.get(AiCache, h)
    if cached is not None:
        try:
            return _apply_threshold(ClassifyResult.model_validate(cached.result), cached.model)
        except ValidationError:
            pass  # a bad cache entry is ignored

    if get_settings().ai_mode == "mock" or not groq_client.has_key():
        golden = _golden().get(normalise(text))
        if get_settings().ai_mode == "mock" and golden:
            r = ClassifyResult(translation_en=golden["translation"], category=golden["acceptable"][0]
                               if golden["acceptable"][0] != "NEEDS_REVIEW" else "OTHER", confidence=0.9)
            return _apply_threshold(r, "mock")
        return _rule_outcome(text)

    if _rate_limited(session, user_id):
        return _rule_outcome(text)

    for model in groq_client.classify_models():
        try:
            raw = groq_client.chat_json(model, SYSTEM_PROMPT, user_message(text))
            result = ClassifyResult.model_validate_json(raw)
        except (groq_client.GroqError, ValidationError, ValueError):
            continue  # 429, timeout, bad JSON or unknown category: next model
        session.merge(AiCache(hash=h, model=model, result=result.model_dump()))
        return _apply_threshold(result, model)
    return _rule_outcome(text)
