import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { CityItemFinder } from "@/components/CityItemFinder";
import { CityProgramBoard } from "@/components/CityProgramBoard";
import { ContinueReading, pagesToContinueLinks } from "@/components/ContinueReading";
import { CorrectionWidget } from "@/components/CorrectionWidget";
import { HaulerCta } from "@/components/HaulerCta";
import { ZipNearList } from "@/components/ZipNearList";
import {
  cityItemHref,
  countyHhwHref,
  getCity,
  getCityHighIntentGuides,
  getCityIndexedFacilities,
  getCityPages,
  getCityProgramGroups,
  getCountyHhwForCity,
  getCtrOverride,
  getIndexablePages,
  getSiblingCities,
  getZipHubs,
} from "@/lib/data";
import { absoluteUrl, breadcrumbJsonLd, pageMetadata } from "@/lib/seo";
import { cityHubDescription, cityHubTitle } from "@/lib/snippets";

type Props = { params: Promise<{ state: string; city: string }> };

export async function generateStaticParams() {
  const pages = getIndexablePages();
  const seen = new Set<string>();
  const params: { state: string; city: string }[] = [];
  for (const p of pages) {
    const key = `${p.state_slug}/${p.city_slug}`;
    if (seen.has(key)) continue;
    seen.add(key);
    params.push({ state: p.state_slug, city: p.city_slug });
  }
  const { getCities } = await import("@/lib/data");
  for (const c of getCities()) {
    const key = `${c.state_slug}/${c.city_slug}`;
    if (seen.has(key)) continue;
    seen.add(key);
    params.push({ state: c.state_slug, city: c.city_slug });
  }
  return params;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { state, city } = await params;
  const place = getCity(state, city);
  if (!place) return {};
  const guides = getCityPages(state, city).filter((p) => p.indexable);
  const path = `/${place.state_slug}/${place.city_slug}`;
  if (!guides.length) {
    return pageMetadata({
      title: `${place.city}, ${place.state} — research pending`,
      description: `We have not published verified disposal guides for ${place.city} yet.`,
      path,
      index: false,
    });
  }
  const override = getCtrOverride(path);
  return pageMetadata({
    title: override?.title ?? cityHubTitle(place.city, place.state),
    description: override?.description ?? cityHubDescription(place.city, place.state, guides.length),
    path,
  });
}

export default async function CityHubPage({ params }: Props) {
  const { state, city } = await params;
  const place = getCity(state, city);
  if (!place) notFound();
  const guides = getCityPages(state, city);
  const indexable = guides.filter((p) => p.indexable);
  const programs = getCityProgramGroups(state, city);
  const siblingCities = getSiblingCities(state, city, 8);
  const zips = getZipHubs().filter(
    (z) => z.city_slug === city && z.state_slug === state && z.indexable,
  );
  const countyHhw = getCountyHhwForCity(state, city);
  const featured = getCityHighIntentGuides(state, city, 8);
  const dropOffs = getCityIndexedFacilities(city);

  const programListLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: `${place.city}, ${place.state} disposal programs`,
    itemListElement: programs.map((g, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: `${g.label} in ${place.city}`,
      url: absoluteUrl(`/${place.state_slug}/${place.city_slug}#${g.key}`),
    })),
  };

  return (
    <div className="shell page">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(
            breadcrumbJsonLd([
              { name: "Cities", path: "/cities" },
              { name: place.state, path: `/${place.state_slug}` },
              { name: place.city, path: `/${place.state_slug}/${place.city_slug}` },
            ]),
          ),
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(programListLd) }}
      />
      <nav className="crumb-row" aria-label="Breadcrumb">
        <Link href="/cities">Cities</Link>
        <span>/</span>
        <Link href={`/${place.state_slug}`}>{place.state}</Link>
        <span>/</span>
        <span>{place.city}</span>
      </nav>

      <header className="prose">
        <h1>
          {place.city}, {place.state}
        </h1>
        {guides.length ? (
          <p>
            Verified dump, bulky pickup, HHW, and e-waste programs in {place.city} — {indexable.length}{" "}
            indexable city guides, with related items grouped on the program board.{" "}
            <Link href="/cities">All verified cities</Link>
          </p>
        ) : (
          <p>
            We have not finished city-specific research for {place.city} yet. We do not publish statewide
            filler as local advice.{" "}
            <Link href="/cities">See cities with verified guides</Link>
          </p>
        )}
      </header>

      {countyHhw ? (
        <p>
          Outside {place.city} limits?{" "}
          <Link href={countyHhwHref(countyHhw)}>
            {countyHhw.county} household hazardous waste
          </Link>{" "}
          is the suburban / county program.
        </p>
      ) : null}

      {featured.length ? (
        <ContinueReading
          id="high-intent"
          heading={`High-intent ${place.city} guides`}
          lead="Mattress, bulky, HHW, and e-waste — the city rules residents actually search."
          links={pagesToContinueLinks(featured, "item")}
        />
      ) : null}

      {dropOffs.length ? (
        <section className="city-dropoffs">
          <h2>Verified drop-offs in {place.city}</h2>
          <p className="muted">
            Named dumps, transfer stations, and HHW sites tied to this city’s research. Confirm hours
            on the official source.
          </p>
          <ul className="facility-result-list">
            {dropOffs.slice(0, 8).map((row) => (
              <li key={row.slug}>
                <Link href={`/centers/${row.slug}`}>
                  <strong>{row.f.name}</strong>
                </Link>
                <span>
                  {row.f.facility_type}
                  {row.f.address ? ` · ${row.f.address}` : ""}
                </span>
                {row.f.hours ? <span>Hours: {row.f.hours}</span> : null}
              </li>
            ))}
          </ul>
          {dropOffs.length > 8 ? (
            <p>
              <Link href="/centers">All centers by ZIP</Link>
            </p>
          ) : null}
        </section>
      ) : null}

      {guides.length ? <CityProgramBoard city={place.city} groups={programs} /> : null}

      {guides.length ? <HaulerCta city={place.city} stateSlug={place.state_slug} /> : null}

      {guides.length ? (
        <CityItemFinder
          city={place.city}
          guides={guides.map((p) => ({
            item_slug: p.item_slug,
            item_name: p.item_name,
            category: p.category,
            state_slug: p.state_slug,
            city_slug: p.city_slug,
            badge: p.badge,
            href: cityItemHref(p),
          }))}
        />
      ) : (
        <section className="trust-panel">
          <h2>Not researched yet</h2>
          <p>
            Suggest an official {place.city} source below and we will review it before publishing any local
            guide.
          </p>
        </section>
      )}

      {zips.length ? (
        <ZipNearList
          zips={zips.map((z) => ({
            zip: z.zip,
            state_slug: z.state_slug,
            city_slug: z.city_slug,
            lat: z.lat,
            lng: z.lng,
          }))}
          cityCenter={{ lat: place.lat, lng: place.lng }}
        />
      ) : null}

      {siblingCities.length ? (
        <ContinueReading
          id="other-state-cities"
          heading={`Other ${place.state} cities`}
          lead="Keep browsing verified metros — each city has its own program rules."
          links={siblingCities.map((c) => ({
            href: `/${c.state_slug}/${c.city_slug}`,
            title: c.city,
            meta: `${getCityPages(c.state_slug, c.city_slug).length} guides`,
          }))}
        />
      ) : null}

      <CorrectionWidget
        city={place.city}
        stateSlug={place.state_slug}
        citySlug={place.city_slug}
      />
    </div>
  );
}
