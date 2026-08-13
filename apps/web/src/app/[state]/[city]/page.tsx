import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { CityItemFinder } from "@/components/CityItemFinder";
import { ContinueReading } from "@/components/ContinueReading";
import { CorrectionWidget } from "@/components/CorrectionWidget";
import { HaulerCta } from "@/components/HaulerCta";
import { ZipNearList } from "@/components/ZipNearList";
import {
  getCity,
  getCityHighIntentGuides,
  getCityPages,
  getCtrOverride,
  getIndexablePages,
  getSiblingCities,
  getZipHubs,
} from "@/lib/data";
import { breadcrumbJsonLd, pageMetadata } from "@/lib/seo";
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
  const guides = getCityPages(state, city);
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
  const indexable = getCityPages(state, city);
  const starters = getCityHighIntentGuides(state, city, 10);
  const siblingCities = getSiblingCities(state, city, 8);
  const zips = getZipHubs().filter(
    (z) => z.city_slug === city && z.state_slug === state && z.indexable,
  );

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
        {indexable.length ? (
          <p>
            {indexable.length} verified guides for dump and transfer drop-off, bulky pickup, HHW, and e-waste
            in {place.city}. Start with a common item, or search everything below.{" "}
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

      {indexable.length ? (
        <ContinueReading
          id="popular-in-city"
          heading={`Popular in ${place.city}`}
          lead="Most-searched hard-to-trash items — tap through for the local answer."
          links={starters.map((p) => ({
            href: `/${p.state_slug}/${p.city_slug}/dispose/${p.item_slug}`,
            title: p.item_name,
            meta: p.category,
          }))}
        />
      ) : null}

      {indexable.length ? <HaulerCta city={place.city} stateSlug={place.state_slug} /> : null}

      {indexable.length ? (
        <CityItemFinder
          city={place.city}
          guides={indexable.map((p) => ({
            item_slug: p.item_slug,
            item_name: p.item_name,
            category: p.category,
            state_slug: p.state_slug,
            city_slug: p.city_slug,
            badge: p.badge,
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
