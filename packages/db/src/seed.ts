import { readFileSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { createDb } from "./client";
import { disposalPages, geoPlaces, items, rules, facilities } from "./schema";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");

function readJson<T>(rel: string): T {
  return JSON.parse(readFileSync(resolve(root, rel), "utf8")) as T;
}

async function main() {
  const db = createDb();
  const itemRows = readJson<Array<Record<string, unknown>>>("data/items.json");
  const cities = existsSync(resolve(root, "data/geo/cities.json"))
    ? readJson<Array<Record<string, unknown>>>("data/geo/cities.json")
    : readJson<Array<Record<string, unknown>>>("data/geo/ca_cities.json");
  const zips = existsSync(resolve(root, "data/geo/zips.json"))
    ? readJson<Array<Record<string, unknown>>>("data/geo/zips.json")
    : existsSync(resolve(root, "data/geo/ca_zips.json"))
      ? readJson<Array<Record<string, unknown>>>("data/geo/ca_zips.json")
      : [];
  const ruleRows = existsSync(resolve(root, "data/rules/all.json"))
    ? readJson<Array<Record<string, unknown>>>("data/rules/all.json")
    : readJson<Array<Record<string, unknown>>>("data/rules/ca.json");
  const facilityRows = existsSync(resolve(root, "data/facilities/all.json"))
    ? readJson<Array<Record<string, unknown>>>("data/facilities/all.json")
    : readJson<Array<Record<string, unknown>>>("data/facilities/ca.json");
  const pages = existsSync(resolve(root, "data/resolved/pages.json"))
    ? readJson<Array<Record<string, unknown>>>("data/resolved/pages.json")
    : [];

  await db.delete(disposalPages);
  await db.delete(rules);
  await db.delete(facilities);
  await db.delete(geoPlaces);
  await db.delete(items);

  await db.insert(items).values(
    itemRows.map((i) => ({
      slug: String(i.slug),
      name: String(i.name),
      category: String(i.category),
      hazardDefault: String(i.hazard_default),
      badgeDefault: String(i.badge_default),
      feeBandDefault: String(i.fee_band_default),
      curbsideDefault: Boolean(i.curbside_default),
      facilityTypeDefault: String(i.facility_type_default),
      summaryDefault: String(i.summary_default),
    })),
  );

  await db.insert(geoPlaces).values(
    [
      ...cities.map((c) => ({
        zip: null as string | null,
        city: String(c.city),
        citySlug: String(c.city_slug),
        state: String(c.state),
        stateSlug: String(c.state_slug),
        lat: Number(c.lat),
        lng: Number(c.lng),
        population: Number(c.population ?? 0),
      })),
      ...zips.map((z) => ({
        zip: String(z.zip),
        city: String(z.city),
        citySlug: String(z.city_slug),
        state: String(z.state),
        stateSlug: String(z.state_slug),
        lat: Number(z.lat),
        lng: Number(z.lng),
        population: Number(z.population ?? 0),
      })),
    ].slice(0, 5000),
  );

  const mappedRules = ruleRows.map((r) => ({
    itemSlug: String(r.item_slug),
    state: String(r.state),
    citySlug: (r.city_slug as string | null) ?? null,
    zip: (r.zip as string | null) ?? null,
    isCurbsideAllowed: r.is_curbside_allowed as boolean | null,
    nearestFacilityType: (r.nearest_facility_type as string | null) ?? null,
    commonDisposalFee: (r.common_disposal_fee as string | null) ?? null,
    badge: (r.badge as string | null) ?? null,
    hazardRating: (r.hazard_rating as string | null) ?? null,
    answer: (r.answer as string | null) ?? null,
    stepsJson: JSON.stringify(r.steps ?? []),
    faqsJson: JSON.stringify(r.faqs ?? []),
    sourceUrl: String(r.source_url),
    sourceName: String(r.source_name),
    lastVerifiedAt: new Date(String(r.last_verified_at)),
    reviewedBy: (r.reviewed_by as string | null) ?? "editorial",
    needsReview: Boolean(r.needs_review ?? false),
  }));
  for (let i = 0; i < mappedRules.length; i += 100) {
    await db.insert(rules).values(mappedRules.slice(i, i + 100));
  }

  if (facilityRows.length) {
    await db.insert(facilities).values(
      facilityRows.map((f) => ({
        name: String(f.name),
        facilityType: String(f.facility_type),
        citySlug: String(f.city_slug),
        state: String(f.state),
        zip: (f.zip as string | null) ?? null,
        address: (f.address as string | null) ?? null,
        lat: f.lat != null ? Number(f.lat) : null,
        lng: f.lng != null ? Number(f.lng) : null,
        sourceUrl: (f.source_url as string | null) ?? null,
      })),
    );
  }

  if (pages.length) {
    const mappedPages = pages.map((p) => ({
      stateSlug: String(p.state_slug),
      citySlug: String(p.city_slug),
      zip: (p.zip as string | null) ?? null,
      itemSlug: String(p.item_slug),
      city: String(p.city),
      state: String(p.state),
      itemName: String(p.item_name),
      category: String(p.category),
      isCurbsideAllowed: Boolean(p.is_curbside_allowed),
      nearestFacilityType: String(p.nearest_facility_type),
      commonDisposalFee: String(p.common_disposal_fee),
      badge: String(p.badge),
      hazardRating: String(p.hazard_rating),
      answer: String(p.answer),
      stepsJson: JSON.stringify(p.steps ?? []),
      faqsJson: JSON.stringify(p.faqs ?? []),
      ruleSourceLevel: String(p.rule_source_level),
      sourceUrl: (p.source_url as string | null) ?? null,
      sourceName: (p.source_name as string | null) ?? null,
      lastVerifiedAt: p.last_verified_at ? new Date(String(p.last_verified_at)) : null,
      lat: p.lat != null ? Number(p.lat) : null,
      lng: p.lng != null ? Number(p.lng) : null,
      indexable: Boolean(p.indexable),
      needsReview: Boolean(p.needs_review ?? false),
    }));
    for (let i = 0; i < mappedPages.length; i += 50) {
      await db.insert(disposalPages).values(mappedPages.slice(i, i + 50));
    }
  }

  console.log(`Seeded ${itemRows.length} items, ${ruleRows.length} rules, ${pages.length} pages`);
  process.exit(0);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
