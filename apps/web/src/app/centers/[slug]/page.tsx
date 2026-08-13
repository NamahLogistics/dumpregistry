import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { cityItemHref, getCities, getFacilities, getItem, getItems } from "@/lib/data";
import { absoluteUrl, breadcrumbJsonLd, facilitySlug, pageMetadata } from "@/lib/seo";
import { clipAtWord } from "@/lib/snippets";

type Props = { params: Promise<{ slug: string }> };

type IndexedFacility = {
  f: ReturnType<typeof getFacilities>[number];
  city: ReturnType<typeof getCities>[number];
  slug: string;
};

let indexedFacilityRows: IndexedFacility[] | null = null;
let indexedFacilityBySlug: Map<string, IndexedFacility> | null = null;

function indexedFacilities() {
  if (indexedFacilityRows) return indexedFacilityRows;
  const cities = new Map(getCities().map((c) => [c.city_slug, c]));
  const seen = new Set<string>();
  const rows: IndexedFacility[] = [];
  for (const f of getFacilities()) {
    if (f.lat == null || f.lng == null) continue;
    const city = cities.get(f.city_slug);
    if (!city) continue;
    const slug = facilitySlug(f);
    if (seen.has(slug)) continue;
    seen.add(slug);
    rows.push({ f, city, slug });
  }
  indexedFacilityRows = rows;
  return rows;
}

function facilityBySlug(slug: string) {
  if (!indexedFacilityBySlug) {
    indexedFacilityBySlug = new Map(indexedFacilities().map((row) => [row.slug, row]));
  }
  return indexedFacilityBySlug.get(slug);
}

export async function generateStaticParams() {
  return indexedFacilities().map((row) => ({ slug: row.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const row = facilityBySlug(slug);
  if (!row) return { robots: { index: false, follow: false } };
  const { f, city } = row;
  return pageMetadata({
    title: clipAtWord(`${f.name} — ${city.city}, ${city.state}`, 60),
    description: `${f.facility_type} at ${f.address || city.city}. Hours, accepted materials, and the official program source.`,
    path: `/centers/${slug}`,
  });
}

export default async function FacilityDetailPage({ params }: Props) {
  const { slug } = await params;
  const row = facilityBySlug(slug);
  if (!row) notFound();
  const { f, city } = row;
  const materials = (f.accepted_materials || [])
    .map((s) => getItem(s))
    .filter(Boolean);

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    name: f.name,
    description: f.facility_type,
    url: absoluteUrl(`/centers/${slug}`),
    telephone: f.phone || undefined,
    address: f.address
      ? {
          "@type": "PostalAddress",
          streetAddress: f.address,
          addressLocality: city.city,
          addressRegion: f.state || city.state,
          postalCode: f.zip || undefined,
          addressCountry: "US",
        }
      : undefined,
    geo:
      f.lat != null && f.lng != null
        ? {
            "@type": "GeoCoordinates",
            latitude: f.lat,
            longitude: f.lng,
          }
        : undefined,
    openingHours: f.hours || undefined,
  };

  return (
    <div className="shell page">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(
            breadcrumbJsonLd([
              { name: "Centers", path: "/centers" },
              { name: f.name, path: `/centers/${slug}` },
            ]),
          ),
        }}
      />

      <nav className="crumb-row" aria-label="Breadcrumb">
        <Link href="/centers">Centers</Link>
        <span>/</span>
        <span>{f.name}</span>
      </nav>

      <header className="prose">
        <p className="eyebrow">{f.facility_type}</p>
        <h1>{f.name}</h1>
        <p>
          Verified drop-off tied to DumpRegistry research for{" "}
          <Link href={`/${city.state_slug}/${city.city_slug}`}>
            {city.city}, {city.state}
          </Link>
          . Confirm hours and acceptance on the official source before you go.
        </p>
      </header>

      <section className="facility-detail-specs">
        {f.address ? (
          <p>
            <strong>Address:</strong> {f.address}
          </p>
        ) : null}
        {f.hours ? (
          <p>
            <strong>Hours:</strong> {f.hours}
          </p>
        ) : null}
        {f.phone ? (
          <p>
            <strong>Phone:</strong> <a href={`tel:${f.phone}`}>{f.phone}</a>
          </p>
        ) : null}
        {f.zip ? (
          <p>
            <strong>ZIP:</strong> {f.zip}
          </p>
        ) : null}
        {f.source_url ? (
          <p>
            <strong>Official source:</strong>{" "}
            <a href={f.source_url} target="_blank" rel="noopener noreferrer">
              {f.source_url.replace(/^https?:\/\//, "").slice(0, 64)}
            </a>
          </p>
        ) : null}
      </section>

      {materials.length ? (
        <section>
          <h2>Materials often accepted</h2>
          <ul className="hub-grid">
            {materials.map((item) =>
              item ? (
                <li key={item.slug} style={{ listStyle: "none" }}>
                  <Link
                    className="hub-link"
                    href={cityItemHref({
                      state_slug: city.state_slug,
                      city_slug: city.city_slug,
                      item_slug: item.slug,
                      category: item.category,
                    })}
                  >
                    {item.name}
                    <span className="hub-link-meta">
                      {item.category} · {city.city} guide
                    </span>
                  </Link>
                </li>
              ) : null,
            )}
          </ul>
        </section>
      ) : (
        <p className="muted">
          Material acceptance varies — check the official source. Browse all{" "}
          <Link href="/materials">{getItems().length} materials</Link>.
        </p>
      )}

      <p style={{ marginTop: "1.5rem" }}>
        <Link href="/centers">← All centers</Link>
        {" · "}
        <Link href={`/${city.state_slug}/${city.city_slug}`}>
          {city.city} dump, bulky & HHW
        </Link>
      </p>
    </div>
  );
}
