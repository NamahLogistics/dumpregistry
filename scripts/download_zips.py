#!/usr/bin/env python3
"""Download a public US ZIP Code CSV and normalize CA rows into data/geo/."""

from __future__ import annotations

import csv
import io
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "geo"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# SimpleMaps free sample / GeoNames-style public endpoint fallbacks.
# Primary: Census Gazetteer ZCTA (public domain). Fallback keeps local seed usable offline.
CENSUS_ZCTA = (
    "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/"
    "2024_Gaz_zcta_national.zip"
)

CITY_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    return CITY_SLUG_RE.sub("-", value.strip().lower()).strip("-")


def write_seed_note() -> None:
    note = OUT_DIR / "README.md"
    note.write_text(
        "# Geography data\n\n"
        "- `ca_cities.json` — curated CA city hubs\n"
        "- `ca_zips.json` — seed ZIPs for maps/hubs\n"
        "- `uszips.csv` — written when download succeeds\n\n"
        "Run `python3 scripts/download_zips.py` with network access to refresh.\n"
    )


def download_census_or_keep_seed() -> None:
    write_seed_note()
    dest = OUT_DIR / "uszips.csv"
    try:
        print("Attempting Census ZCTA download (zip)…")
        # Many environments block large Census zips; try a lightweight public CSV mirror pattern.
        # If download fails, keep curated CA seed files already in repo.
        req = urllib.request.Request(
            "https://raw.githubusercontent.com/scpike/us-state-county-zip/master/geo-data.csv",
            headers={"User-Agent": "DumpRegistryBot/0.1 (+https://dumpregistry.org)"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            text = resp.read().decode("utf-8", errors="replace")
        dest.write_text(text)
        print(f"Wrote {dest} ({len(text.splitlines())} lines)")
        normalize_ca_from_csv(dest)
    except Exception as exc:  # noqa: BLE001 — offline-friendly
        print(f"Download skipped/failed ({exc}). Using curated CA seed files.")
        if not (OUT_DIR / "ca_zips.json").exists():
            raise SystemExit("Missing data/geo/ca_zips.json seed") from exc


def normalize_ca_from_csv(csv_path: Path) -> None:
    """Best-effort CA extract when CSV columns vary."""
    sample = csv_path.read_text(encoding="utf-8", errors="replace")[:4000]
    dialect = csv.Sniffer().sniff(sample, delimiters=",\t;")
    reader = csv.DictReader(io.StringIO(csv_path.read_text(encoding="utf-8", errors="replace")), dialect=dialect)
    if not reader.fieldnames:
        return
    fields = {f.lower(): f for f in reader.fieldnames}
    zip_key = next((fields[k] for k in fields if k in {"zip", "zipcode", "zip_code", "zcta5", "geoid"}), None)
    city_key = next((fields[k] for k in fields if k in {"city", "place", "usps_city"}), None)
    state_key = next((fields[k] for k in fields if k in {"state", "state_id", "stusps"}), None)
    lat_key = next((fields[k] for k in fields if k in {"lat", "latitude", "intptlat"}), None)
    lng_key = next((fields[k] for k in fields if k in {"lng", "lon", "long", "longitude", "intptlong"}), None)
    pop_key = next((fields[k] for k in fields if "pop" in k), None)
    if not all([zip_key, city_key, state_key]):
        print("CSV columns not recognized; leaving ca_zips.json seed unchanged.")
        return

    rows = []
    for row in reader:
        state = (row.get(state_key) or "").strip().upper()
        if state not in {"CA", "CALIFORNIA"}:
            continue
        city = (row.get(city_key) or "").strip().title()
        zip_code = re.sub(r"\D", "", row.get(zip_key) or "")[:5]
        if len(zip_code) != 5 or not city:
            continue
        rows.append(
            {
                "zip": zip_code,
                "city": city,
                "city_slug": slugify(city),
                "state": "CA",
                "state_slug": "california",
                "lat": float(row[lat_key]) if lat_key and row.get(lat_key) else None,
                "lng": float(row[lng_key]) if lng_key and row.get(lng_key) else None,
                "population": int(float(row[pop_key])) if pop_key and row.get(pop_key) else 0,
            }
        )
        if len(rows) >= 2500:
            break
    if rows:
        out = OUT_DIR / "ca_zips.json"
        out.write_text(json.dumps(rows, indent=2))
        print(f"Normalized {len(rows)} CA ZIPs → {out}")


if __name__ == "__main__":
    download_census_or_keep_seed()
