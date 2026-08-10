#!/usr/bin/env python3
"""Validate rule JSON and print coverage stats."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load_rules():
    preferred = DATA / "rules" / "all.json"
    if preferred.exists():
        return json.loads(preferred.read_text())
    rows = []
    for name in ("ca.json", "national.json"):
        path = DATA / "rules" / name
        if path.exists():
            rows.extend(json.loads(path.read_text()))
    return rows


def main() -> None:
    rules = load_rules()
    items = {i["slug"] for i in json.loads((DATA / "items.json").read_text())}
    required = ["item_slug", "state", "source_url", "source_name", "last_verified_at", "answer"]
    errors = []
    for i, r in enumerate(rules):
        for key in required:
            if not r.get(key):
                errors.append(f"rule[{i}] missing {key}")
        if r["item_slug"] not in items:
            errors.append(f"rule[{i}] unknown item {r['item_slug']}")
        fee = r.get("common_disposal_fee")
        if fee and len(str(fee)) > 80:
            errors.append(f"rule[{i}] fee too long ({len(str(fee))})")
    state_count = sum(1 for r in rules if not r.get("city_slug"))
    city_count = sum(1 for r in rules if r.get("city_slug"))
    states = sorted({r["state"] for r in rules if r.get("city_slug")})
    print(f"Rules OK: {len(rules)} (state={state_count}, city={city_count}) states={states}")
    if errors:
        print("ERRORS:")
        for e in errors[:40]:
            print(" -", e)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
