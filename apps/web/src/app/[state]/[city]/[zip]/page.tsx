import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { MapPlaceholder } from "@/components/MapPlaceholder";
import { getCityPages, getZipHub } from "@/lib/data";

type Props = { params: Promise<{ state: string; city: string; zip: string }> };

export async function generateStaticParams() {
  const { getZipHubs } = await import("@/lib/data");
  return getZipHubs().map((z) => ({
    state: z.state_slug,
    city: z.city_slug,
    zip: z.zip,
  }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { state, city, zip } = await params;
  const hub = getZipHub(state, city, zip);
  if (!hub) return {};
  return {
    title: `ZIP ${hub.zip} disposal context — ${hub.city}, ${hub.state}`,
    description: `Facilities and item guides near ZIP ${hub.zip} in ${hub.city}.`,
  };
}

export default async function ZipHubPage({ params }: Props) {
  const { state, city, zip } = await params;
  const hub = getZipHub(state, city, zip);
  if (!hub) notFound();
  const guides = getCityPages(state, city).filter((p) => p.indexable);

  return (
    <div className="shell page">
      <header className="prose">
        <h1>
          ZIP {hub.zip} · {hub.city}, {hub.state}
        </h1>
        <p>
          Facility orientation for this ZIP. Item answers live on city guides — we only create ZIP hubs when
          coordinates help humans navigate.{" "}
          <Link href={`/${hub.state_slug}/${hub.city_slug}`}>{hub.city} hub</Link>
        </p>
      </header>
      <MapPlaceholder
        lat={hub.lat}
        lng={hub.lng}
        city={`${hub.city} ${hub.zip}`}
        facilities={hub.facilities}
      />
      <section>
        <h2>Item guides for {hub.city}</h2>
        <div className="hub-grid">
          {guides.map((p) => (
            <Link
              key={p.item_slug}
              className="hub-link"
              href={`/${p.state_slug}/${p.city_slug}/dispose/${p.item_slug}`}
            >
              {p.item_name}
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
