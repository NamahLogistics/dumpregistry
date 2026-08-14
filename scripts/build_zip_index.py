#!/usr/bin/env python3
"""Build a compact US ZIP → [state, lat, lng] index for partner coverage matching.

Writes data/geo/zip_index.json. Tries public sources; always merges local hub ZIPs.
"""

from __future__ import annotations

import csv
import io
import json
import re
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "geo" / "zip_index.json"
UA = {"User-Agent": "DumpRegistryBot/0.1 (+https://dumpregistry.org)"}

GEONAMES_US = "https://download.geonames.org/export/zip/US.zip"
SCPIKE_CSV = "https://raw.githubusercontent.com/scpike/us-state-county-zip/master/geo-data.csv"
MILLBJ_JSON = "https://raw.githubusercontent.com/millbj92/US-Zip-Codes-JSON/master/USCities.json"

ZIP_RE = re.compile(r"^\d{5}$")


def fetch(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def put(index: dict[str, list], zip_code: str, state: str, lat: float | None, lng: float | None) -> None:
    zip_code = re.sub(r"\D", "", zip_code or "")[:5]
    if not ZIP_RE.match(zip_code):
        return
    state = (state or "").strip().upper()
    if len(state) == 2 and lat is not None and lng is not None:
        index[zip_code] = [state, round(float(lat), 5), round(float(lng), 5)]


def from_geonames(index: dict[str, list]) -> int:
    raw = fetch(GEONAMES_US)
    before = len(index)
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        names = zf.namelist()
        name = next((n for n in names if n.upper().endswith("US.TXT")), None)
        if name is None:
            name = next((n for n in names if n.lower().endswith(".txt") and "readme" not in n.lower()), names[0])
        with zf.open(name) as fh:
            for line in io.TextIOWrapper(fh, encoding="utf-8", errors="replace"):
                parts = line.rstrip("\n").split("\t")
                if len(parts) < 11:
                    continue
                put(index, parts[1], parts[4], float(parts[9]), float(parts[10]))
    return len(index) - before


def from_scpike(index: dict[str, list]) -> int:
    text = fetch(SCPIKE_CSV).decode("utf-8", errors="replace")
    before = len(index)
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        return 0
    fields = {f.lower(): f for f in reader.fieldnames}
    zip_key = next((fields[k] for k in fields if k in {"zip", "zipcode", "zip_code", "zcta5", "geoid"}), None)
    state_key = next((fields[k] for k in fields if k in {"state", "state_id", "stusps", "state_abbr"}), None)
    lat_key = next((fields[k] for k in fields if k in {"lat", "latitude", "intptlat"}), None)
    lng_key = next((fields[k] for k in fields if k in {"lng", "lon", "long", "longitude", "intptlong"}), None)
    if not zip_key or not state_key:
        return 0
    for row in reader:
        try:
            lat = float(row[lat_key]) if lat_key and row.get(lat_key) else None
            lng = float(row[lng_key]) if lng_key and row.get(lng_key) else None
        except (TypeError, ValueError):
            lat, lng = None, None
        put(index, row.get(zip_key) or "", row.get(state_key) or "", lat, lng)
    return len(index) - before


def from_millbj(index: dict[str, list]) -> int:
    rows = json.loads(fetch(MILLBJ_JSON, timeout=120).decode("utf-8", errors="replace"))
    before = len(index)
    if not isinstance(rows, list):
        return 0
    for row in rows:
        zip_code = str(row.get("zip_code") or row.get("zip") or "").zfill(5)
        state = str(row.get("state_id") or row.get("state") or "")
        lat = row.get("latitude") if row.get("latitude") is not None else row.get("lat")
        lng = row.get("longitude") if row.get("longitude") is not None else row.get("lng")
        put(index, zip_code, state, lat, lng)
    return len(index) - before


def from_local(index: dict[str, list]) -> int:
    before = len(index)
    geo = ROOT / "data" / "geo"
    for name in ("zips.json", "ca_zips.json", "cities.json"):
        path = geo / name
        if not path.exists():
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            continue
        for row in rows:
            zip_code = str(row.get("zip") or "")
            state = str(row.get("state") or "")
            lat = row.get("lat")
            lng = row.get("lng")
            if zip_code:
                put(index, zip_code, state, lat, lng)
    hubs = ROOT / "data" / "resolved" / "zip_hubs.json"
    if hubs.exists():
        for row in json.loads(hubs.read_text(encoding="utf-8")):
            put(index, str(row.get("zip") or ""), str(row.get("state") or ""), row.get("lat"), row.get("lng"))
    return len(index) - before


def main() -> None:
    index: dict[str, list] = {}
    local_n = from_local(index)
    print(f"Local hubs: +{local_n} (now {len(index)})")
    try:
        n = from_geonames(index)
        print(f"GeoNames US: +{n} (now {len(index)})")
    except Exception as exc:  # noqa: BLE001
        print(f"GeoNames skipped ({exc})")
        try:
            n = from_scpike(index)
            print(f"scpike CSV: +{n} (now {len(index)})")
        except Exception as exc2:  # noqa: BLE001
            print(f"scpike skipped ({exc2})")
            try:
                n = from_millbj(index)
                print(f"millbj JSON: +{n} (now {len(index)})")
            except Exception as exc3:  # noqa: BLE001
                print(f"millbj skipped ({exc3})")
    if len(index) < 50:
        raise SystemExit("zip_index too small — check network or local geo files")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(index, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {len(index)} ZIPs → {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
