"""Golden-set evaluation: python -m backend.app.ai.eval  (Doc3 section 11).

Always scores the keyword rules. Scores each Groq model only when GROQ_API_KEY is set and
AI_MODE=live, so without a key the table honestly shows 'not run'. Put the result table in the TDD."""
from __future__ import annotations

import json
import time

from pydantic import ValidationError

from backend.app.ai import groq_client
from backend.app.ai.classify import GOLDEN, ClassifyResult
from backend.app.ai.prompt import SYSTEM_PROMPT, user_message
from backend.app.ai.rules import classify_rules
from backend.app.config import get_config, get_settings


def _score(rows: list[tuple[str, float]], gold: list[dict]) -> dict:
    ok = sum(1 for (cat, _), g in zip(rows, gold, strict=True) if cat in g["acceptable"])
    review = sum(1 for cat, _ in rows if cat == "NEEDS_REVIEW")
    lat = sorted(t for _, t in rows)
    p95 = lat[min(len(lat) - 1, int(0.95 * len(lat)))] if lat else 0.0
    return {"accuracy": ok / len(gold), "needs_review": review / len(gold), "p95_ms": round(p95 * 1000, 1),
            "errors": [g["text"] for (cat, _), g in zip(rows, gold, strict=True) if cat not in g["acceptable"]]}


def run_rules(gold: list[dict]) -> dict:
    rows = []
    for g in gold:
        t0 = time.perf_counter()
        rows.append((classify_rules(g["text"]).category, time.perf_counter() - t0))
    return _score(rows, gold)


def run_model(model: str, gold: list[dict]) -> dict:
    rows = []
    thr = get_config().ai_confidence_min
    for g in gold:
        t0 = time.perf_counter()
        try:
            r = ClassifyResult.model_validate_json(groq_client.chat_json(model, SYSTEM_PROMPT, user_message(g["text"])))
            cat = r.category if r.confidence >= thr else "NEEDS_REVIEW"
        except (groq_client.GroqError, ValidationError, ValueError):
            cat = "ERROR"
        rows.append((cat, time.perf_counter() - t0))
    return _score(rows, gold)


def main() -> None:
    gold = json.loads(GOLDEN.read_text(encoding="utf-8"))
    results = {"rules": run_rules(gold)}
    live = groq_client.has_key() and get_settings().ai_mode == "live"
    if live:
        for m in groq_client.classify_models():
            results[m] = run_model(m, gold)
    print(f"Golden set: {len(gold)} notes (labels not yet native-reviewed, A-12)\n")
    print("| Classifier | Accuracy | Needs review | p95 latency (ms) |\n|---|---|---|---|")
    for name, r in results.items():
        print(f"| {name} | {r['accuracy']:.0%} | {r['needs_review']:.0%} | {r['p95_ms']} |")
    if not live:
        print("\nGroq models: NOT RUN (no GROQ_API_KEY or AI_MODE != live).")
    print("\nRule errors:", results["rules"]["errors"])


if __name__ == "__main__":
    main()
