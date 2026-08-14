import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { FacilityMap } from "@/components/FacilityMap";
import { FaqSection, faqJsonLd } from "@/components/FaqSection";
import {
  cityItemHref,
  getCityIndexedFacilities,
  getFacilityBySlug,
  getIndexedFacilities,
  getItem,
  getItems,
  getNearbyIndexedFacilities,
} from "@/lib/data";
import { formatMiles, mapsDirectionsUrl, milesBetween } from "@/lib/geo";
import { absoluteUrl, breadcrumbJsonLd, pageMetadata } from "@/lib/seo";
import { clipAtWord } from "@/lib/snippets";
import type { Faq } from "@/lib/types";

type Props = { params: Promise<{ slug: string }> };

export async function generateStaticParams() {
  return getIndexedFacilities().map((row) => ({ slug: row.slug }));
}

function facilityFaqs(opts: {
  name: string;
  city: string;
  state: string;
  hours?: string | null;
  phone?: string | null;
  materials: string[];
  sourceUrl?: string | null;
}): Faq[] {
  const faqs: Faq[] = [];
  if (opts.hours) {
    faqs.push({
      q: `When is ${opts.name} open?`,
      a: `Listed hours: ${opts.hours}. Confirm on the official source before you drive — holiday and event hours change.`,
    });
  }
  if (opts.phone) {
    faqs.push({
      q: `Is there a phone number for ${opts.name}?`,
      a: `Call ${opts.phone} for load rules, residency, and whether you need an appointment.`,
    });
  }
  if (opts.materials.length) {
    faqs.push({
      q: `What can I drop off at ${opts.name}?`,
      a: `This site is listed for ${opts.materials.join(", ")}. Acceptance still depends on the official program — not this list alone.`,
    });
  }
  faqs.push({
    q: `Do I need to live in ${opts.city} to use ${opts.name}?`,
    a: `Many municipal dumps and HHW sites are resident-only or appointment-only. Check the official ${opts.city}, ${opts.state} program page before you load the vehicle.`,
  });
  if (opts.sourceUrl) {
    faqs.push({
      q: `Where is the official listing for ${opts.name}?`,
      a: `DumpRegistry cites the originating program. Confirm hours and fees on that official page, not a third-party directory.`,
    });
  }
  return faqs;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const row = getFacilityBySlug(slug);
  if (!row) return { robots: { index: false, follow: false } };
  const { f, city } = row;
  const where = f.address ? `${f.address}` : `${city.city}, ${city.state}`;
  return pageMetadata({
    title: clipAtWord(`${f.name} — ${city.city}, ${city.state}`, 60),
    description: clipAtWord(
      `${f.name} (${f.facility_type}) at ${where}. Hours, phone, accepted materials, and the official program source.`,
      160,
    ),
    path: `/centers/${slug}`,
  });
}

export default async function FacilityDetailPage({ params }: Props) {
  const { slug } = await params;
  const row = getFacilityBySlug(slug);
  if (!row) notFound();
  const { f, city } = row;
  const materials = (f.accepted_materials || [])
    .map((s) => getItem(s))
    .filter(Boolean);
  const nearby = getNearbyIndexedFacilities(slug, 6);
  const citySites = getCityIndexedFacilities(city.city_slug).filter((r) => r.slug !== slug);
  const directions = mapsDirectionsUrl({
    address: f.address,
    lat: f.lat,
    lng: f.lng,
  });
  const mapFacilities = [f, ...nearby.map((n) => n.f)];
  const faqs = facilityFaqs({
    name: f.name,
    city: city.city,
    state: city.state,
    hours: f.hours,
    phone: f.phone,
    materials: materials.map((item) => item!.name),
    sourceUrl: f.source_url,
  });

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "CivicStructure",
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
              { name: city.city, path: `/${city.state_slug}/${city.city_slug}` },
              { name: f.name, path: `/centers/${slug}` },
            ]),
          ),
        }}
      />
      {faqs.length ? (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd(faqs)) }}
        />
      ) : null}

      <nav className="crumb-row" aria-label="Breadcrumb">
        <Link href="/centers">Centers</Link>
        <span>/</span>
        <Link href={`/${city.state_slug}/${city.city_slug}`}>
          {city.city}, {city.state}
        </Link>
        <span>/</span>
        <span>{f.name}</span>
      </nav>

      <header className="prose">
        <p className="eyebrow">{f.facility_type}</p>
        <h1>{f.name}</h1>
        <p>
          Official drop-off for{" "}
          <Link href={`/${city.state_slug}/${city.city_slug}`}>
            {city.city}, {city.state}
          </Link>
          . City dispose pages own the rule for each item. This page is the place: address, hours,
          and the originating program. Confirm before you go.
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
        <p className="facility-detail-actions">
          {directions ? (
            <a href={directions} target="_blank" rel="noopener noreferrer">
              Directions
            </a>
          ) : null}
          <Link href={f.zip ? `/centers?zip=${encodeURIComponent(f.zip)}` : "/centers"}>
            ZIP finder
          </Link>
          <Link href={`/${city.state_slug}/${city.city_slug}`}>
            {city.city} dump, bulky & HHW
          </Link>
        </p>
      </section>

      <FacilityMap
        city={city.city}
        lat={f.lat}
        lng={f.lng}
        facilities={mapFacilities}
        heading={`${f.name} and nearby drop-offs`}
      />

      {materials.length ? (
        <section>
          <h2>Materials often accepted</h2>
          <p className="muted">
            Tied to this site’s listing — still confirm on the official source. Each link is the{" "}
            {city.city} city rule, not a national guess.
          </p>
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
                    {item.name} in {city.city}
                    <span className="hub-link-meta">
                      {item.category} · city guide
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

      {nearby.length ? (
        <section>
          <h2>Other drop-offs within 40 miles</h2>
          <ul className="facility-result-list">
            {nearby.map((n) => {
              const mi =
                f.lat != null && f.lng != null && n.f.lat != null && n.f.lng != null
                  ? milesBetween(
                      { lat: f.lat, lng: f.lng },
                      { lat: n.f.lat, lng: n.f.lng },
                    )
                  : null;
              return (
                <li key={n.slug}>
                  <Link href={`/centers/${n.slug}`}>
                    <strong>{n.f.name}</strong>
                  </Link>
                  <span>
                    {n.f.facility_type}
                    {n.city.city !== city.city ? ` · ${n.city.city}, ${n.city.state}` : ""}
                    {mi != null ? ` · ${formatMiles(mi)}` : ""}
                  </span>
                  {n.f.address ? <span>{n.f.address}</span> : null}
                </li>
              );
            })}
          </ul>
        </section>
      ) : citySites.length ? (
        <section>
          <h2>Other {city.city} drop-offs</h2>
          <ul className="facility-result-list">
            {citySites.slice(0, 6).map((n) => (
              <li key={n.slug}>
                <Link href={`/centers/${n.slug}`}>
                  <strong>{n.f.name}</strong>
                </Link>
                <span>{n.f.facility_type}</span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <FaqSection faqs={faqs} />

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
