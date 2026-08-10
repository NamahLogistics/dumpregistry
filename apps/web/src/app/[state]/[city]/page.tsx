import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getCity, getCityPages, getZipHubs } from "@/lib/data";

type Props = { params: Promise<{ state: string; city: string }> };

export async function generateStaticParams() {
  const { getCities } = await import("@/lib/data");
  return getCities().map((c) => ({ state: c.state_slug, city: c.city_slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { state, city } = await params;
  const place = getCity(state, city);
  if (!place) return {};
  return {
    title: `Dispose of hard items in ${place.city}, ${place.state}`,
    description: `Local disposal guides for ${place.city}, ${place.state}.`,
  };
}

export default async function CityHubPage({ params }: Props) {
  const { state, city } = await params;
  const place = getCity(state, city);
  if (!place) notFound();
  const pages = getCityPages(state, city);
  const indexable = pages.filter((p) => p.indexable);
  const zips = getZipHubs().filter((z) => z.city_slug === city && z.state_slug === state);

  return (
    <div className="shell page">
      <header className="prose">
        <h1>
          {place.city}, {place.state}
        </h1>
        <p>
          Start with a verified item guide. ZIP hubs help with nearby facility context.{" "}
          <Link href="/california">All California cities</Link>
        </p>
      </header>

      <section>
        <h2>Verified guides</h2>
        <div className="hub-grid">
          {indexable.map((p) => (
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

      {zips.length ? (
        <section>
          <h2>ZIP hubs</h2>
          <div className="hub-grid">
            {zips.map((z) => (
              <Link
                key={z.zip}
                className="hub-link"
                href={`/${z.state_slug}/${z.city_slug}/${z.zip}`}
              >
                {z.zip}
              </Link>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
