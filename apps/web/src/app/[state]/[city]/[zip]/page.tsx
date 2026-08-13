import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { CityItemFinder } from "@/components/CityItemFinder";
import { ContinueReading } from "@/components/ContinueReading";
import { FacilityMap } from "@/components/FacilityMap";
import { getCityHighIntentGuides, getCityPages, getZipHub, getZipHubs } from "@/lib/data";
import { pageMetadata } from "@/lib/seo";

type Props = { params: Promise<{ state: string; city: string; zip: string }> };

export async function generateStaticParams() {
  return getZipHubs()
    .filter((z) => z.indexable)
    .map((z) => ({
      state: z.state_slug,
      city: z.city_slug,
      zip: z.zip,
    }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { state, city, zip } = await params;
  const hub = getZipHub(state, city, zip);
  if (!hub) return { robots: { index: false, follow: false } };
  return pageMetadata({
    title: `${hub.city} ZIP ${hub.zip} drop-off`,
    description: `Verified drop-off sites and item guides near ZIP ${hub.zip} in ${hub.city}, ${hub.state}.`,
    path: `/${hub.state_slug}/${hub.city_slug}/${hub.zip}`,
  });
}

export default async function ZipHubPage({ params }: Props) {
  const { state, city, zip } = await params;
  const hub = getZipHub(state, city, zip);
  if (!hub) notFound();
  const guides = getCityPages(state, city);
  const starters = getCityHighIntentGuides(state, city, 8);
  const otherZips = getZipHubs().filter(
    (z) =>
      z.indexable &&
      z.state_slug === state &&
      z.city_slug === city &&
      z.zip !== hub.zip,
  );

  return (
    <div className="shell page">
      <nav className="crumb-row" aria-label="Breadcrumb">
        <Link href="/cities">Cities</Link>
        <span>/</span>
        <Link href={`/${hub.state_slug}/${hub.city_slug}`}>{hub.city}</Link>
        <span>/</span>
        <span>ZIP {hub.zip}</span>
      </nav>

      <header className="prose">
        <h1>
          ZIP {hub.zip} · {hub.city}, {hub.state}
        </h1>
        <p>
          Facility orientation for this ZIP. Open an item guide next for the full disposal answer.{" "}
          <Link href={`/${hub.state_slug}/${hub.city_slug}`}>{hub.city} hub</Link>
        </p>
      </header>

      <ContinueReading
        id="zip-starters"
        heading={`Start with a guide in ${hub.city}`}
        lead="ZIP pages orient facilities — item pages give the step-by-step answer."
        links={starters.map((p) => ({
          href: `/${p.state_slug}/${p.city_slug}/dispose/${p.item_slug}`,
          title: p.item_name,
          meta: p.category,
        }))}
      />

      <FacilityMap
        city={`${hub.city} ${hub.zip}`}
        lat={hub.lat}
        lng={hub.lng}
        facilities={hub.facilities}
        zipRefs={[{ zip: hub.zip, lat: hub.lat, lng: hub.lng }]}
      />

      {otherZips.length ? (
        <ContinueReading
          id="other-zips"
          heading={`Other ${hub.city} ZIP hubs`}
          links={otherZips.slice(0, 8).map((z) => ({
            href: `/${z.state_slug}/${z.city_slug}/${z.zip}`,
            title: `ZIP ${z.zip}`,
            meta: hub.city,
          }))}
        />
      ) : null}

      <CityItemFinder
        city={hub.city}
        guides={guides.map((p) => ({
          item_slug: p.item_slug,
          item_name: p.item_name,
          category: p.category,
          state_slug: p.state_slug,
          city_slug: p.city_slug,
          badge: p.badge,
        }))}
      />
    </div>
  );
}
