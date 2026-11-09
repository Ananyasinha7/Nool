"""Writes contract/openapi.json from the FastAPI app (no server needed). Run from the repo root:
python scripts/export_openapi.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.main import app  # noqa: E402


def render() -> str:
    # sort_keys + trailing newline keep the file byte-stable so CI can diff it
    return json.dumps(app.openapi(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    (ROOT / "contract" / "openapi.json").write_text(render(), encoding="utf-8")
    print("wrote contract/openapi.json")
