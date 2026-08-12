#!/usr/bin/env python3
"""Facility inventory audit — first-line quality gate as the list grows.

Checks (errors fail CI by default; warnings are reported):
  - soft facilities present (should be hard-only)
  - unknown city_slug / missing required fields
  - city_slug state vs facility.state (with border-metro allowlist)
  - distance from metro centroid (far = warn/error)
  - address state token vs facility.state (corruption detector)
  - missing / non-official source_url
  - duplicate (city_slug, name) and (city_slug, address)

Usage:
  python3 scripts/audit_facilities.py
  python3 scripts/audit_facilities.py --json data/ops/facility_audit.json
  python3 scripts/audit_facilities.py --fail-on warning   # stricter
  python3 scripts/audit_facilities.py --max-distance-warn 120 --max-distance-error 250

Exit 0 if no findings at/above --fail-on severity.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.facility_quality import is_hard_facility  # noqa: E402

FAC_PATH = ROOT / "data" / "facilities" / "all.json"
CITIES_PATH = ROOT / "data" / "geo" / "cities.json"
DEFAULT_REPORT = ROOT / "data" / "ops" / "facility_audit.json"

# Border metros where facility.state may differ from city.state (collar counties).
BORDER_OK: dict[str, frozenset[str]] = {
    "portland": frozenset({"OR", "WA"}),
    "kansas-city": frozenset({"KS", "MO"}),
    "st-louis": frozenset({"MO", "IL"}),
    "chicago": frozenset({"IL", "IN", "WI"}),
    "cincinnati": frozenset({"OH", "KY", "IN"}),
    "louisville": frozenset({"KY", "IN"}),
    "omaha": frozenset({"NE", "IA"}),
    "memphis": frozenset({"TN", "AR", "MS"}),
    "philadelphia": frozenset({"PA", "NJ", "DE"}),
    "new-york": frozenset({"NY", "NJ", "CT"}),
    "washington": frozenset({"DC", "MD", "VA"}),
    "virginia-beach": frozenset({"VA", "NC"}),
    "charlotte": frozenset({"NC", "SC"}),
    "chattanooga": frozenset({"TN", "GA"}),
    "texarkana": frozenset({"TX", "AR"}),
    "boston": frozenset({"MA", "RI", "NH", "CT"}),
    "baltimore": frozenset({"MD", "PA", "DE", "VA"}),
    "pittsburgh": frozenset({"PA", "OH", "WV"}),
    "spokane": frozenset({"WA", "ID"}),
    "minneapolis": frozenset({"MN", "WI"}),
    "detroit": frozenset({"MI", "OH"}),
    "buffalo": frozenset({"NY", "PA"}),
    "providence": frozenset({"RI", "MA", "CT"}),
}

# Known solid-waste portals that are not *.gov but are official enough.
SOURCE_ALLOWLIST = frozenset({
    "rcwaste.org",
    "oclandfills.com",
    "mwatoday.com",
    "nrswa.org",
    "swalco.org",
    "swaco.org",
    "cuyahogarecycles.org",
    "willcountygreen.com",
    "ramseyrecycles.com",
    "themdc.org",
    "swa.org",
    "rirrc.org",
    "metrecycle.com",
    "niswmd.org",
    "cleanla.lacounty.gov",  # lacounty.gov variant handled by .gov
    "environment.westchestergov.com",
    "westchestergov.com",
    "denvergov.org",
    "vbgov.com",
    "oakgov.com",
    "muni.org",
    "cityoftulsa.org",
    "sedgwickcounty.org",
    "countyofkane.org",
    "jccal.org",
    "bakercountyfl.org",
    "marionfl.org",
    "flcounties.com",
    "kernpublicworks.com",
})

US_STATE_ABBR = frozenset({
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL",
    "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT",
    "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC",
})

ADDR_STATE_RE = re.compile(
    r",\s*([A-Z]{2})\s+\d{5}(?:-\d{4})?\s*$|,?\s+([A-Z]{2})\s+\d{5}",
    re.I,
)


@dataclass
class Finding:
    severity: str  # error | warning | info
    code: str
    city_slug: str
    name: str
    detail: str
    source_url: str = ""
    miles: float | None = None


@dataclass
class Report:
    total_facilities: int = 0
    hard: int = 0
    soft: int = 0
    cities: int = 0
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    by_code: dict[str, int] = field(default_factory=dict)
    findings: list[dict[str, Any]] = field(default_factory=list)


def haversine_mi(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 3958.8
    p = math.radians
    dlat = p(lat2 - lat1)
    dlon = p(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p(lat1)) * math.cos(p(lat2)) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(min(1.0, a)))


def norm_addr(addr: str) -> str:
    a = (addr or "").lower()
    a = re.sub(r"\bst\b\.?", "street", a)
    a = re.sub(r"\bave\b\.?", "avenue", a)
    a = re.sub(r"\brd\b\.?", "road", a)
    a = re.sub(r"\bblvd\b\.?", "boulevard", a)
    a = re.sub(r"\bdr\b\.?", "drive", a)
    a = re.sub(r"\bln\b\.?", "lane", a)
    return re.sub(r"[^a-z0-9]", "", a)[:60]


def host_of(url: str) -> str:
    return urlparse(url or "").netloc.lower().removeprefix("www.")


def is_official_source(url: str) -> bool:
    if not url:
        return False
    host = host_of(url)
    if not host:
        return False
    if host in SOURCE_ALLOWLIST:
        return True
    parts = host.split(".")
    if parts[-1] == "gov" or (len(parts) >= 2 and parts[-2] == "gov"):
        return True
    if host.endswith(".us") and any(p.endswith("county") or p in ("state", "city") for p in parts):
        return True
    # *.lacounty.gov, *.westchestergov.com style
    if "gov" in host.replace(".", " ").split():
        return True
    if host.endswith("gov.com") or "countygov" in host or host.endswith("gov.org"):
        return True
    return False


def address_state(addr: str) -> str | None:
    m = ADDR_STATE_RE.search(addr or "")
    if not m:
        return None
    token = (m.group(1) or m.group(2) or "").upper()
    return token if token in US_STATE_ABBR else None


def state_ok(city_slug: str, city_state: str, fac_state: str) -> bool:
    if not fac_state:
        return False
    if fac_state == city_state:
        return True
    allowed = BORDER_OK.get(city_slug)
    return bool(allowed and fac_state in allowed and city_state in allowed)


def audit(
    facilities: list[dict],
    cities: dict[str, dict],
    *,
    max_distance_warn: float,
    max_distance_error: float,
) -> list[Finding]:
    findings: list[Finding] = []

    by_name: dict[tuple[str, str], list[dict]] = defaultdict(list)
    by_addr: dict[tuple[str, str], list[dict]] = defaultdict(list)

    for row in facilities:
        slug = (row.get("city_slug") or "").strip()
        name = (row.get("name") or "").strip()
        state = (row.get("state") or "").strip().upper()
        addr = row.get("address") or ""
        url = row.get("source_url") or ""
        lat, lng = row.get("lat"), row.get("lng")

        if not slug or slug not in cities:
            findings.append(Finding("error", "unknown_city", slug or "?", name, "city_slug not in cities.json", url))
            continue

        city = cities[slug]

        if not is_hard_facility(row):
            findings.append(Finding("error", "soft_facility", slug, name, "fails is_hard_facility hard bar", url))

        if not name:
            findings.append(Finding("error", "missing_name", slug, name, "empty name", url))

        if not url:
            findings.append(Finding("error", "missing_source", slug, name, "missing source_url", url))
        elif not is_official_source(url):
            findings.append(
                Finding(
                    "warning",
                    "non_official_source",
                    slug,
                    name,
                    f"source host not .gov/allowlisted: {host_of(url)}",
                    url,
                )
            )

        miles: float | None = None
        if lat is None or lng is None:
            findings.append(Finding("error", "missing_coords", slug, name, "missing lat/lng", url))
        else:
            try:
                miles = haversine_mi(float(city["lat"]), float(city["lng"]), float(lat), float(lng))
            except (TypeError, ValueError):
                findings.append(Finding("error", "bad_coords", slug, name, f"invalid lat/lng: {lat},{lng}", url))
                miles = None
            if miles is not None:
                if miles > max_distance_error:
                    findings.append(
                        Finding(
                            "error",
                            "distance_extreme",
                            slug,
                            name,
                            f"{miles:.0f} mi from {slug} centroid (>{max_distance_error:.0f})",
                            url,
                            miles,
                        )
                    )
                elif miles > max_distance_warn:
                    findings.append(
                        Finding(
                            "warning",
                            "distance_far",
                            slug,
                            name,
                            f"{miles:.0f} mi from {slug} centroid (>{max_distance_warn:.0f})",
                            url,
                            miles,
                        )
                    )

        if state and not state_ok(slug, city["state"], state):
            # Far + wrong state = error; nearby collar mis-file = warning (review queue).
            sev = "error" if (miles is not None and miles > max_distance_warn) else "warning"
            findings.append(
                Finding(
                    sev,
                    "state_mismatch",
                    slug,
                    name,
                    f"facility state {state} vs city {city['state']} (not in border allowlist)",
                    url,
                    miles,
                )
            )

        addr_st = address_state(addr)
        if addr_st and state and addr_st != state:
            # Corruption if address state disagrees with facility.state.
            # Border metros may still be valid if address state is an allowed collar state.
            border = BORDER_OK.get(slug, frozenset())
            if addr_st in border and city["state"] in border:
                findings.append(
                    Finding(
                        "warning",
                        "address_state_conflict",
                        slug,
                        name,
                        f"address implies {addr_st} but facility.state={state} — sync state field",
                        url,
                        miles,
                    )
                )
            else:
                findings.append(
                    Finding(
                        "error",
                        "address_state_conflict",
                        slug,
                        name,
                        f"address implies {addr_st} but facility.state={state}",
                        url,
                        miles,
                    )
                )

        by_name[(slug, name.lower())].append(row)
        na = norm_addr(addr)
        if na and len(na) >= 12:
            by_addr[(slug, na)].append(row)

    for (slug, key), rows in by_name.items():
        if len(rows) > 1:
            findings.append(
                Finding(
                    "warning",
                    "duplicate_name",
                    slug,
                    rows[0].get("name") or key,
                    f"{len(rows)} rows share city_slug+name",
                    rows[0].get("source_url") or "",
                )
            )

    for (slug, key), rows in by_addr.items():
        if len(rows) > 1:
            names = " | ".join((r.get("name") or "?")[:40] for r in rows[:3])
            findings.append(
                Finding(
                    "info",
                    "duplicate_address",
                    slug,
                    rows[0].get("name") or key,
                    f"{len(rows)} rows share address: {names}",
                    rows[0].get("source_url") or "",
                )
            )

    return findings


def build_report(facilities: list[dict], findings: list[Finding]) -> Report:
    hard = sum(1 for f in facilities if is_hard_facility(f))
    soft = len(facilities) - hard
    cities = len({f.get("city_slug") for f in facilities})
    by_code = Counter(f.code for f in findings)
    sev = Counter(f.severity for f in findings)
    return Report(
        total_facilities=len(facilities),
        hard=hard,
        soft=soft,
        cities=cities,
        error_count=sev.get("error", 0),
        warning_count=sev.get("warning", 0),
        info_count=sev.get("info", 0),
        by_code=dict(sorted(by_code.items(), key=lambda x: (-x[1], x[0]))),
        findings=[asdict(f) for f in sorted(findings, key=lambda x: (x.severity != "error", x.severity != "warning", x.code, x.city_slug, x.name))],
    )


def print_summary(report: Report, *, limit: int) -> None:
    print(
        f"facilities={report.total_facilities} hard={report.hard} soft={report.soft} "
        f"cities={report.cities}"
    )
    print(
        f"findings: errors={report.error_count} warnings={report.warning_count} "
        f"info={report.info_count}"
    )
    if report.by_code:
        print("by_code:")
        for code, n in list(report.by_code.items())[:20]:
            print(f"  {code}: {n}")
    shown = 0
    for f in report.findings:
        if f["severity"] == "info":
            continue
        if shown >= limit:
            rest = sum(1 for x in report.findings if x["severity"] != "info") - shown
            if rest > 0:
                print(f"  … {rest} more (see --json report)")
            break
        miles = f" ({f['miles']:.0f} mi)" if f.get("miles") is not None else ""
        print(f"  [{f['severity']}] {f['code']} [{f['city_slug']}] {f['name'][:55]}{miles}")
        print(f"           {f['detail']}")
        shown += 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", type=Path, default=DEFAULT_REPORT, help="Write JSON report path")
    ap.add_argument("--no-json", action="store_true", help="Skip writing JSON report")
    ap.add_argument("--fail-on", choices=("error", "warning", "info", "never"), default="error")
    ap.add_argument("--max-distance-warn", type=float, default=100.0)
    ap.add_argument("--max-distance-error", type=float, default=180.0)
    ap.add_argument("--limit", type=int, default=40, help="Max findings to print")
    args = ap.parse_args()

    facilities = json.loads(FAC_PATH.read_text())
    cities = {c["city_slug"]: c for c in json.loads(CITIES_PATH.read_text())}

    findings = audit(
        facilities,
        cities,
        max_distance_warn=args.max_distance_warn,
        max_distance_error=args.max_distance_error,
    )
    report = build_report(facilities, findings)
    print_summary(report, limit=args.limit)

    if not args.no_json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(asdict(report), indent=2, ensure_ascii=False) + "\n")
        print(f"wrote {args.json}")

    rank = {"error": 3, "warning": 2, "info": 1}
    if args.fail_on == "never":
        return 0
    threshold = rank[args.fail_on]
    worst = max((rank[f.severity] for f in findings), default=0)
    return 1 if worst >= threshold else 0


if __name__ == "__main__":
    raise SystemExit(main())
