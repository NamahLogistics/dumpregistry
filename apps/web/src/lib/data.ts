import { readFileSync } from "node:fs";
import path from "node:path";
import { dataRoot } from "./paths";
import type { SnippetOverride } from "./snippets";
import type { City, DisposalPage, Facility, Item, ZipHub } from "./types";

function readJson<T>(rel: string): T {
  const full = path.join(dataRoot(), rel);
  return JSON.parse(readFileSync(full, "utf8")) as T;
}

let cache: {
  items?: Item[];
  cities?: City[];
  pages?: DisposalPage[];
  zipHubs?: ZipHub[];
  facilities?: Facility[];
  ctrOverrides?: Record<string, SnippetOverride>;
} = {};

export function getItems(): Item[] {
  cache.items ??= readJson<Item[]>("items.json");
  return cache.items;
}

export function getCities(): City[] {
  if (!cache.cities) {
    try {
      cache.cities = readJson<City[]>("geo/cities.json");
    } catch {
      cache.cities = readJson<City[]>("geo/ca_cities.json");
    }
  }
  return cache.cities;
}

export function getStates() {
  const bySlug = new Map<string, { state_slug: string; state: string; population: number }>();
  for (const c of getCities()) {
    const cur = bySlug.get(c.state_slug);
    if (!cur) {
      bySlug.set(c.state_slug, {
        state_slug: c.state_slug,
        state: c.state,
        population: c.population ?? 0,
      });
    } else {
      cur.population += c.population ?? 0;
    }
  }
  return [...bySlug.values()].sort((a, b) => b.population - a.population);
}

export function getPages(): DisposalPage[] {
  cache.pages ??= readJson<DisposalPage[]>("resolved/pages.json");
  return cache.pages;
}

export function getZipHubs(): ZipHub[] {
  cache.zipHubs ??= readJson<ZipHub[]>("resolved/zip_hubs.json");
  return cache.zipHubs;
}

export function getFacilities(): Facility[] {
  cache.facilities ??= readJson<Facility[]>("facilities/all.json");
  return cache.facilities;
}

/** City dispose guides that cover a material — for encyclopedia deep links. */
export function getMaterialCityGuides(itemSlug: string, limit = 24): DisposalPage[] {
  return getIndexablePages()
    .filter((p) => p.item_slug === itemSlug)
    .sort((a, b) => a.city.localeCompare(b.city))
    .slice(0, limit);
}

export function getMaterialGuideCount(itemSlug: string): number {
  return getIndexablePages().filter((p) => p.item_slug === itemSlug).length;
}

export type MaterialOverview = {
  overview: string;
  prep_steps: string[];
  common_mistakes: string[];
};

export function getMaterialOverview(itemSlug: string): MaterialOverview | null {
  try {
    const all = readJson<Record<string, MaterialOverview>>("materials/overviews.json");
    return all[itemSlug] ?? null;
  } catch {
    return null;
  }
}

export function getItem(slug: string) {
  return getItems().find((i) => i.slug === slug);
}

/** GSC CTR rewrites keyed by pathname, e.g. `/texas/austin/dispose/mattress`. */
export function getCtrOverride(pathname: string): SnippetOverride | undefined {
  if (!cache.ctrOverrides) {
    try {
      cache.ctrOverrides = readJson<Record<string, SnippetOverride>>("seo/ctr_overrides.json");
    } catch {
      cache.ctrOverrides = {};
    }
  }
  return cache.ctrOverrides[pathname];
}

export function getCity(stateSlug: string, citySlug: string) {
  return getCities().find((c) => c.state_slug === stateSlug && c.city_slug === citySlug);
}

export function getPage(stateSlug: string, citySlug: string, itemSlug: string) {
  return getPages().find(
    (p) =>
      p.state_slug === stateSlug &&
      p.city_slug === citySlug &&
      p.item_slug === itemSlug &&
      p.indexable &&
      p.rule_source_level === "city",
  );
}

export function getIndexablePages() {
  return getPages().filter((p) => p.indexable && p.rule_source_level === "city");
}

export function getCityPages(stateSlug: string, citySlug: string) {
  return getIndexablePages().filter((p) => p.state_slug === stateSlug && p.city_slug === citySlug);
}

export function getZipHub(stateSlug: string, citySlug: string, zip: string) {
  return getZipHubs().find(
    (z) =>
      z.state_slug === stateSlug &&
      z.city_slug === citySlug &&
      z.zip === zip &&
      z.indexable,
  );
}

/** Cities/items that have at least one verified city guide — for the wizard. */
export function cityKey(stateSlug: string, citySlug: string) {
  return `${stateSlug}/${citySlug}`;
}

export function getWizardOptions() {
  const pages = getIndexablePages();
  const covered = new Set(pages.map((p) => cityKey(p.state_slug, p.city_slug)));
  const itemSlugs = new Set(pages.map((p) => p.item_slug));
  const cities = getCities()
    .filter((c) => covered.has(cityKey(c.state_slug, c.city_slug)))
    .map((c) => ({
      city_slug: c.city_slug,
      city: c.city,
      state_slug: c.state_slug,
      state: c.state,
      key: cityKey(c.state_slug, c.city_slug),
    }))
    .sort((a, b) => a.city.localeCompare(b.city) || a.state.localeCompare(b.state));
  const items = getItems()
    .filter((i) => itemSlugs.has(i.slug))
    .map((i) => ({ slug: i.slug, name: i.name, category: i.category }));
  const itemsByCity: Record<string, string[]> = {};
  for (const p of pages) {
    const key = cityKey(p.state_slug, p.city_slug);
    itemsByCity[key] ??= [];
    itemsByCity[key].push(p.item_slug);
  }
  return { cities, items, itemsByCity };
}

export function badgeLabel(badge: string) {
  switch (badge) {
    case "BANNED_FROM_LANDFILLS":
      return "Banned from landfills";
    case "ACCEPTED_IN_BLUE_BIN":
      return "Accepted in diversion stream";
    case "SPECIAL_HANDLING":
      return "Special handling required";
    default:
      return badge.replaceAll("_", " ");
  }
}

/** High-intent items — good first clicks for hubs and continue-reading. */
export const HIGH_INTENT_ITEMS = [
  "mattress",
  "refrigerator",
  "television",
  "paint-latex",
  "lithium-battery",
  "sofa",
  "tires",
  "air-conditioner",
  "computer-monitor",
  "propane-tank",
] as const;

export function getRelatedInCity(page: DisposalPage, limit = 6): DisposalPage[] {
  const others = getCityPages(page.state_slug, page.city_slug).filter(
    (p) => p.item_slug !== page.item_slug,
  );
  const sameCat = others.filter((p) => p.category === page.category);
  const high = others.filter((p) =>
    (HIGH_INTENT_ITEMS as readonly string[]).includes(p.item_slug),
  );
  const seen = new Set<string>();
  const out: DisposalPage[] = [];
  for (const p of [...sameCat, ...high, ...others]) {
    if (seen.has(p.item_slug)) continue;
    seen.add(p.item_slug);
    out.push(p);
    if (out.length >= limit) break;
  }
  return out;
}

export function getSameItemOtherCities(page: DisposalPage, limit = 6): DisposalPage[] {
  return getIndexablePages()
    .filter(
      (p) =>
        p.item_slug === page.item_slug &&
        !(p.state_slug === page.state_slug && p.city_slug === page.city_slug),
    )
    .sort((a, b) => a.city.localeCompare(b.city))
    .slice(0, limit);
}

export function getSiblingCities(stateSlug: string, citySlug: string, limit = 8) {
  const covered = new Set(
    getIndexablePages()
      .filter((p) => p.state_slug === stateSlug)
      .map((p) => p.city_slug),
  );
  return getCities()
    .filter((c) => c.state_slug === stateSlug && covered.has(c.city_slug) && c.city_slug !== citySlug)
    .sort((a, b) => (b.population ?? 0) - (a.population ?? 0))
    .slice(0, limit);
}

export function getCityHighIntentGuides(stateSlug: string, citySlug: string, limit = 10) {
  const bySlug = new Map(getCityPages(stateSlug, citySlug).map((p) => [p.item_slug, p]));
  const pinned = HIGH_INTENT_ITEMS.map((slug) => bySlug.get(slug)).filter(Boolean) as DisposalPage[];
  if (pinned.length >= limit) return pinned.slice(0, limit);
  const rest = getCityPages(stateSlug, citySlug).filter(
    (p) => !(HIGH_INTENT_ITEMS as readonly string[]).includes(p.item_slug),
  );
  return [...pinned, ...rest].slice(0, limit);
}
