#!/usr/bin/env python3
"""Generate async email drafts for hauler acquisition (no phone calls).

Writes data/ops/hauler_outreach_drafts.jsonl — import into your mail tool / Instantly / etc.
Does not send email. Does not scrape inboxes.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "ops" / "hauler_outreach_drafts.jsonl"

# Seed list: replace/add public business emails you collect from websites, chambers, etc.
# Keep this file local; do not commit purchased lists with personal data if restricted.
PROSPECTS = [
    {"company": "Example Junk Co", "email": "dispatch@example.com", "city": "Los Angeles", "state": "CA"},
    {"company": "Example Haul LLC", "email": "jobs@example.com", "city": "Houston", "state": "TX"},
    {"company": "Example Pickup Inc", "email": "info@example.com", "city": "Chicago", "state": "IL"},
]


def draft(p: dict) -> dict:
    city = p["city"]
    subject = f"Free pilot: {city} junk-removal leads from DumpRegistry"
    body = f"""Hi {p["company"]},

DumpRegistry.org publishes city disposal guides. When residents in {city} can’t self-haul, they request pickup on the page.

We’re opening a free pilot: your first 10 qualified {city} leads at $0. Apply (no sales call):

https://www.dumpregistry.org/partners?city={city.replace(" ", "-").lower()}

If {city} isn’t your market, reply with the cities you cover.

— DumpRegistry Partners
"""
    return {
        "to": p["email"],
        "company": p["company"],
        "city": city,
        "state": p["state"],
        "subject": subject,
        "body": body,
        "cta": "https://www.dumpregistry.org/partners",
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(draft(p)) for p in PROSPECTS]
    OUT.write_text("\n".join(lines) + "\n")
    print(f"Wrote {len(lines)} drafts → {OUT}")
    print("Replace PROSPECTS with real public business emails, then import into your ESP.")


if __name__ == "__main__":
    main()
