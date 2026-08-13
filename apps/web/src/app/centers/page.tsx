import type { Metadata } from "next";
import Link from "next/link";
import { CentersFilter } from "@/components/CentersFilter";
import { getCities, getCtrOverride, getFacilities, getItems, getZipHubs } from "@/lib/data";
import { formatMiles, sortByDistance } from "@/lib/geo";
import { facilitySlug, pageMetadata } from "@/lib/seo";

export const metadata: Metadata = pageMetadata({
  title: "Dump, HHW & bulky drop-off near you",
  description:
    "Find verified dump, transfer, HHW, and e-waste drop-off sites by ZIP or material — city-researched, with official program links.",
  path: "/centers",
});

type Props = {
  searchParams: Promise<{ zip?: string; material?: string }>;
};

export default async function CentersPage({ searchParams }: Props) {
  const sp = await searchParams;
  const zip = (sp.zip || "").trim();
  const material = (sp.material || "").trim();
  const items = getItems();
  const cities = getCities();
  const cityBySlug = new Map(cities.map((c) => [c.city_slug, c]));

  let facilities = getFacilities().filter((f) => f.lat != null && f.lng != null);
  if (material) {
    facilities = facilities.filter((f) => (f.accepted_materials || []).includes(material));
  }

  const hub = zip
    ? getZipHubs().find((z) => z.zip === zip && z.lat != null && z.lng != null)
    : null;

  const ranked = hub
    ? sortByDistance(facilities, { lat: hub.lat!, lng: hub.lng! }, (f) =>
        f.lat != null && f.lng != null ? { lat: f.lat, lng: f.lng } : null,
      )
    : facilities
        .map((f) => ({ ...f, distanceMi: null as number | null }))
        .sort((a, b) => a.name.localeCompare(b.name));

  const shown = ranked.slice(0, 40);
  const materialName = items.find((i) => i.slug === material)?.name;

  return (
    <div className="shell page">
      <header className="prose">
        <h1>Drop-off centers</h1>
        <p>
          Authentic finder: {getFacilities().length} verified drop-off sites from official program
          sources (not scraped directories). Coverage grows city-by-city — filter by ZIP and material,
          then confirm hours on the linked official page before you go.
        </p>
      </header>

      <CentersFilter
        initialZip={zip}
        initialMaterial={material}
        items={items.map((i) => ({ slug: i.slug, name: i.name }))}
      />

      <p className="muted">
        {hub
          ? `Sorted by distance from ${zip}${materialName ? ` · filtered for ${materialName}` : ""}.`
          : zip
            ? `ZIP ${zip} is not in our hub index yet — showing ${materialName ? materialName + " " : ""}matches unranked. Try a ZIP from a verified city.`
            : `Showing ${materialName ? materialName + " " : ""}matches${material ? "" : " (all types)"}. Enter a ZIP to sort by distance.`}
      </p>

      <ul className="facility-result-list">
        {shown.map((f) => {
          const city = cityBySlug.get(f.city_slug);
          return (
            <li key={`${f.city_slug}-${f.name}-${f.address || ""}`}>
              <div>
                <strong>{f.name}</strong>
                <span className="muted"> · {f.facility_type}</span>
              </div>
              {f.address ? <div>{f.address}</div> : null}
              <div className="muted">
                {city ? `${city.city}, ${city.state}` : f.state}
                {f.hours ? ` · ${f.hours}` : ""}
                {f.distanceMi != null ? ` · ${formatMiles(f.distanceMi)}` : ""}
              </div>
              <div className="facility-result-links">
                <Link href={`/centers/${facilitySlug(f)}`}>Facility page</Link>
                {f.source_url ? (
                  <a href={f.source_url} target="_blank" rel="noopener noreferrer">
                    Official source
                  </a>
                ) : null}
                {city ? (
                  <Link href={`/${city.state_slug}/${city.city_slug}`}>City guides</Link>
                ) : null}
              </div>
            </li>
          );
        })}
      </ul>

      {shown.length === 0 ? (
        <p>
          No matching centers yet. Try another material, or open a{" "}
          <Link href="/cities">city guide</Link> for the official program path.
        </p>
      ) : null}
    </div>
  );
}
