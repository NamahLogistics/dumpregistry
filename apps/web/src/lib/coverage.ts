import { readFileSync } from "node:fs";
import path from "node:path";
import { milesBetween } from "./geo";
import { dataRoot } from "./paths";

export const MAX_RADIUS_MILES = 150;

type ZipCoord = { state: string; lat: number; lng: number };

let indexCache: Record<string, ZipCoord> | null = null;

function loadZipIndex(): Record<string, ZipCoord> {
  if (indexCache) return indexCache;
  try {
    const raw = JSON.parse(readFileSync(path.join(dataRoot(), "geo/zip_index.json"), "utf8")) as Record<
      string,
      [string, number, number]
    >;
    const map: Record<string, ZipCoord> = {};
    for (const [zip, tuple] of Object.entries(raw)) {
      const [state, lat, lng] = tuple;
      map[zip] = { state, lat, lng };
    }
    indexCache = map;
    return map;
  } catch (err) {
    console.error("[coverage] zip_index.json missing", err);
    indexCache = {};
    return indexCache;
  }
}

export function normalizeZip(raw: unknown): string | null {
  const digits = String(raw ?? "").replace(/\D/g, "");
  if (digits.length < 5) return null;
  return digits.slice(0, 5);
}

export function parseZipList(raw: unknown): string[] {
  const text = String(raw ?? "");
  const found = text.match(/\d{5}/g) ?? [];
  return [...new Set(found.map((z) => normalizeZip(z)).filter((z): z is string => Boolean(z)))];
}

export function lookupZip(zip: string): ZipCoord | null {
  return loadZipIndex()[zip] ?? null;
}

export function expandCoverage(opts: {
  shopZip: string;
  extraZips: string[];
  radiusMiles: number | null;
}): { zips: string[]; summary: string; shopKnown: boolean } {
  const shopZip = normalizeZip(opts.shopZip);
  if (!shopZip) {
    throw new Error("Shop ZIP must be 5 digits");
  }
  const shop = lookupZip(shopZip);
  const set = new Set<string>([shopZip, ...opts.extraZips]);

  const radius =
    opts.radiusMiles != null && Number.isFinite(opts.radiusMiles) ? Math.round(opts.radiusMiles) : null;
  if (radius != null && (radius < 1 || radius > MAX_RADIUS_MILES)) {
    throw new Error(`Radius must be between 1 and ${MAX_RADIUS_MILES} miles`);
  }
  if (radius != null) {
    if (!shop) {
      throw new Error("Shop ZIP is not in the US index — paste the ZIP list instead of using a radius");
    }
    const latDelta = radius / 69;
    const lngDelta = radius / (69 * Math.max(0.2, Math.cos((shop.lat * Math.PI) / 180)));
    for (const [zip, coord] of Object.entries(loadZipIndex())) {
      if (Math.abs(coord.lat - shop.lat) > latDelta) continue;
      if (Math.abs(coord.lng - shop.lng) > lngDelta) continue;
      if (milesBetween(shop, coord) <= radius) set.add(zip);
    }
  }

  const zips = [...set].sort();
  if (!zips.length) throw new Error("Coverage needs at least one ZIP");

  const parts = [`${zips.length} ZIP${zips.length === 1 ? "" : "s"} from ${shopZip}`];
  if (radius) parts.push(`${radius}-mile radius`);
  if (opts.extraZips.length) parts.push(`${opts.extraZips.length} listed`);
  return { zips, summary: parts.join(" · "), shopKnown: Boolean(shop) };
}

export function coverageIncludes(coverageZips: unknown, zip: string): boolean {
  if (!Array.isArray(coverageZips)) {
    if (typeof coverageZips === "string") {
      try {
        return coverageIncludes(JSON.parse(coverageZips), zip);
      } catch {
        return coverageZips.includes(zip);
      }
    }
    return false;
  }
  return coverageZips.some((z) => String(z) === zip);
}
