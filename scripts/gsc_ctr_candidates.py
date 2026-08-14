#!/usr/bin/env python3
"""List GSC title-rewrite candidates — position ≤ 20 only.

Ignores the long tail. Does not write ctr_overrides.json.

Expected CSV columns (Search Console Pages or Queries+Pages export):
  page or landing_page or url
  query (optional)
  clicks
  impressions
  ctr
  position

Usage:
  python3 scripts/gsc_ctr_candidates.py path/to/gsc.csv
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MAX_POSITION = 20.0
MIN_IMPRESSIONS = 10

PAGE_KEYS = ("page", "landing_page", "url", "top_pages")
QUERY_KEYS = ("query", "top_queries")
CLICK_KEYS = ("clicks",)
IMP_KEYS = ("impressions",)
CTR_KEYS = ("ctr",)
POS_KEYS = ("position", "avg_position", "average_position")


def col(row: dict, keys: tuple[str, ...]) -> str:
    lower = {k.lower().strip(): v for k, v in row.items() if k}
    for key in keys:
        if key in lower and lower[key] not in (None, ""):
            return str(lower[key]).strip()
    return ""


def num(raw: str) -> float:
    text = raw.replace("%", "").replace(",", "").strip()
    if not text:
        return 0.0
    return float(text)


def pathname(url: str) -> str:
    raw = url.strip()
    if not raw:
        return ""
    if raw.startswith("/"):
        return raw.split("?")[0] or "/"
    parsed = urlparse(raw)
    path = parsed.path or "/"
    return path.split("?")[0] or "/"


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(
            "Need a Search Console CSV. Export Pages (or Queries) for at least 7 days, "
            f"then: python3 scripts/gsc_ctr_candidates.py export.csv\n"
            f"Only rows with position ≤ {MAX_POSITION:g} are candidates."
        )
    src = Path(sys.argv[1])
    if not src.exists():
        raise SystemExit(f"missing {src}")
    overrides = json.loads((ROOT / "data" / "seo" / "ctr_overrides.json").read_text())
    rows = []
    with src.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames:
            raise SystemExit("CSV has no header")
        for raw in reader:
            pos = num(col(raw, POS_KEYS))
            imps = num(col(raw, IMP_KEYS))
            if pos <= 0 or pos > MAX_POSITION:
                continue
            if imps < MIN_IMPRESSIONS:
                continue
            path = pathname(col(raw, PAGE_KEYS))
            if not path:
                continue
            clicks = num(col(raw, CLICK_KEYS))
            ctr = num(col(raw, CTR_KEYS))
            if ctr > 1:
                ctr = ctr / 100.0
            rows.append(
                {
                    "path": path,
                    "query": col(raw, QUERY_KEYS),
                    "clicks": clicks,
                    "impressions": imps,
                    "ctr": ctr,
                    "position": pos,
                    "has_override": path in overrides,
                }
            )
    rows.sort(key=lambda r: (r["position"], -r["impressions"]))
    print(f"candidates position≤{MAX_POSITION:g} and impressions≥{MIN_IMPRESSIONS}: {len(rows)}")
    for r in rows[:40]:
        print(
            f"  p{r['position']:.1f}  ctr={r['ctr']:.2%}  {r['impressions']:.0f} imp  "
            f"{r['path']}  {r['query'] or '—'}  "
            f"{'override' if r['has_override'] else 'default-title'}"
        )
    if not rows:
        print("No position≤20 rows. Do not rewrite the long tail.")


if __name__ == "__main__":
    main()
