import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ContinueReading } from "@/components/ContinueReading";
import { getCities, getCityHighIntentGuides, getIndexablePages, getStates } from "@/lib/data";
import { pageMetadata } from "@/lib/seo";
import { stateHubDescription, stateHubTitle } from "@/lib/snippets";

type Props = { params: Promise<{ state: string }> };

export async function generateStaticParams() {
  return getStates().map((s) => ({ state: s.state_slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { state } = await params;
  const match = getStates().find((s) => s.state_slug === state);
  if (!match) return { robots: { index: false, follow: false } };
  const cityCount = new Set(
    getIndexablePages()
      .filter((p) => p.state_slug === match.state_slug)
      .map((p) => p.city_slug),
  ).size;
  return pageMetadata({
    title: stateHubTitle(match.state_slug),
    description: stateHubDescription(match.state_slug, cityCount),
    path: `/${match.state_slug}`,
  });
}

export default async function StateHubPage({ params }: Props) {
  const { state } = await params;
  const match = getStates().find((s) => s.state_slug === state);
  if (!match) notFound();

  const pages = getIndexablePages().filter((p) => p.state_slug === state);
  const covered = new Set(pages.map((p) => p.city_slug));
  const cities = getCities()
    .filter((c) => c.state_slug === state)
    .sort((a, b) => (b.population ?? 0) - (a.population ?? 0));
  const ready = cities.filter((c) => covered.has(c.city_slug));
  const pending = cities.filter((c) => !covered.has(c.city_slug));
  const label = state.replaceAll("-", " ");

  return (
    <div className="shell page">
      <header className="prose">
        <h1 style={{ textTransform: "capitalize" }}>{label}</h1>
        <p>
          {pages.length} verified city-program guides across {ready.length} cities. We do not publish statewide
          text as local advice.
        </p>
        <p>
          <Link href="/cities">All verified cities</Link>
        </p>
      </header>

      {ready[0] ? (
        <ContinueReading
          id="state-starters"
          heading={`Popular guides in ${label}`}
          lead="Jump into a high-intent item, then browse related guides in that city."
          links={getCityHighIntentGuides(ready[0].state_slug, ready[0].city_slug, 6).map((p) => ({
            href: `/${p.state_slug}/${p.city_slug}/dispose/${p.item_slug}`,
            title: `${p.item_name}`,
            meta: p.city,
          }))}
        />
      ) : null}

      <section>
        <h2>Verified cities</h2>
        <div className="hub-grid">
          {ready.map((c) => {
            const count = pages.filter((p) => p.city_slug === c.city_slug).length;
            const teasers = getCityHighIntentGuides(c.state_slug, c.city_slug, 3);
            return (
              <div key={c.city_slug} className="city-card">
                <Link className="hub-link city-card-main" href={`/${c.state_slug}/${c.city_slug}`}>
                  <strong>{c.city}</strong>
                  <span className="hub-link-meta">{count} guides</span>
                </Link>
                <div className="city-card-teasers">
                  {teasers.map((p) => (
                    <Link
                      key={p.item_slug}
                      href={`/${p.state_slug}/${p.city_slug}/dispose/${p.item_slug}`}
                    >
                      {p.item_name}
                    </Link>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {pending.length ? (
        <section>
          <h2>Research pending</h2>
          <p>These hubs exist so you can request a source — they have no invented local guides.</p>
          <div className="hub-grid">
            {pending.map((c) => (
              <Link key={c.city_slug} className="hub-link" href={`/${c.state_slug}/${c.city_slug}`}>
                <strong>{c.city}</strong>
                <div>Not researched yet</div>
              </Link>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
