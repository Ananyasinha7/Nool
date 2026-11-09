"""CI guard: the committed contract/openapi.json must equal what the Pydantic models produce now."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_committed_openapi_is_current():
    spec = importlib.util.spec_from_file_location("export_openapi", ROOT / "scripts" / "export_openapi.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    committed = (ROOT / "contract" / "openapi.json").read_text(encoding="utf-8")
    assert committed == mod.render(), "contract is stale: run python scripts/export_openapi.py"


def test_every_api_route_is_in_the_contract():
    import json

    paths = json.loads((ROOT / "contract" / "openapi.json").read_text(encoding="utf-8"))["paths"]
    for p in ("/api/orders", "/api/logs", "/api/warnings/{warning_id}/confirm", "/api/buyer/session",
              "/api/export/weekly", "/api/healthz"):
        assert p in paths
