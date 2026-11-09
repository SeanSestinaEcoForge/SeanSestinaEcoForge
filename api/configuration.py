"""Local, read-only design profiles. All physical parameters carry provenance."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = {"pilot": "pilot-v2.json", "future-node": "future-node-ideas.json"}

def load_config(profile="pilot"):
    if profile not in PROFILES:
        raise ValueError("Unknown profile")
    return json.loads((ROOT / "configs" / PROFILES[profile]).read_text())

def values(section):
    return {key: record["value"] for key, record in section.items()
            if isinstance(record, dict) and "value" in record}
