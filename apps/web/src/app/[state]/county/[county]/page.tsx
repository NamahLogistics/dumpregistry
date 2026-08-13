import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { SourceLink } from "@/components/SourceLink";
import {
  cityItemHref,
  countyHhwHref,
  getCityPages,
  getCountyHhw,
  getCountyHhwHubs,
  getCtrOverride,
} from "@/lib/data";
import { breadcrumbJsonLd, pageMetadata } from "@/lib/seo";
import { countyHhwDescription, countyHhwTitle } from "@/lib/snippets";

type Props = { params: Promise<{ state: string; county: string }> };

const HHW_LINKS = [
  "paint-latex",
  "paint-oil",
  "motor-oil",
  "propane-tank",
  "lithium-battery",
  "household-batteries",
  "antifreeze",
  "fluorescent-bulbs",
  "helium-tank",
  "fire-extinguisher",
] as const;

export async function generateStaticParams() {
  return getCountyHhwHubs().map((h) => ({ state: h.state_slug, county: h.county_slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { state, county } = await params;
  const hub = getCountyHhw(state, county);
  if (!hub) return { robots: { index: false, follow: false } };
  const path = countyHhwHref(hub);
  const override = getCtrOverride(path);
  return pageMetadata({
    title: countyHhwTitle(hub.county, hub.state, override?.title),
    description: override?.description ?? countyHhwDescription(hub),
    path,
    index: hub.indexable,
  });
}

function kindLabel(kind: string): string {
  switch (kind) {
    case "county_distinct":
      return "County program — not the city depot";
    case "county_program":
      return "County / regional HHW";
    case "consolidated":
      return "Consolidated city-county program";
    case "no_county_depot":
      return "No countywide HHW depot";
    default:
      return "Confirm eligibility — city program verified";
  }
}

export default async function CountyHhwPage({ params }: Props) {
  const { state, county } = await params;
  const hub = getCountyHhw(state, county);
  if (!hub) notFound();
  const path = countyHhwHref(hub);
  const leadCity = hub.cities[0];
  const cityPages = leadCity
    ? getCityPages(hub.state_slug, leadCity.city_slug).filter(
        (p) => p.indexable && HHW_LINKS.includes(p.item_slug as (typeof HHW_LINKS)[number]),
      )
    : [];
  const bySlug = new Map(cityPages.map((p) => [p.item_slug, p]));
  const itemLinks = HHW_LINKS.map((slug) => bySlug.get(slug)).filter(Boolean);

  return (
    <div className="shell page">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(
            breadcrumbJsonLd([
              { name: "Counties", path: "/counties" },
              { name: hub.state, path: `/${hub.state_slug}` },
              { name: hub.county, path },
            ]),
          ),
        }}
      />
      <nav className="crumb-row" aria-label="Breadcrumb">
        <Link href="/counties">County HHW</Link>
        <span>/</span>
        <Link href={`/${hub.state_slug}`}>{hub.state}</Link>
        <span>/</span>
        <span>{hub.county}</span>
      </nav>

      <article className="prose">
        <p className="eyebrow">{kindLabel(hub.kind)}</p>
        <h1>
          {hub.county}, {hub.state} household hazardous waste
        </h1>
        <p>
          {hub.program_name}. This page is the suburban / county program for the{" "}
          {hub.cities.map((c) => c.city).join(" / ")} metro — not a “near me” material hub and not
          the city dispose page.
        </p>
        <p>{hub.who_qualifies}</p>
        <p>{hub.city_note}</p>
        {hub.facility ? (
          <p>
            <strong>Where:</strong> {hub.facility}
          </p>
        ) : null}
        <p>
          <strong>How to use it:</strong> {hub.access}
        </p>
        {hub.fee_note ? (
          <p>
            <strong>Cost:</strong> {hub.fee_note} We do not invent fees.
          </p>
        ) : null}
        {hub.accepted_hint ? (
          <p>
            <strong>Typically accepted:</strong> {hub.accepted_hint}
          </p>
        ) : null}
        {hub.not_accepted_hint ? (
          <p>
            <strong>Typically refused:</strong> {hub.not_accepted_hint}
          </p>
        ) : null}
        <p>
          Pesticides, herbicides, pool chemicals, and gasoline belong on this county program when
          the official list says so — they are not a second city bulky day.
        </p>
        {hub.source_url ? (
          <p>
            Official source:{" "}
            <SourceLink url={hub.source_url} title={hub.source_name}>
              {hub.source_name || hub.program_name}
            </SourceLink>
            {hub.last_verified_at ? ` · Verified ${hub.last_verified_at.slice(0, 10)}` : null}
          </p>
        ) : null}
      </article>

      {hub.cities.length ? (
        <section>
          <h2>City dispose pages in this metro</h2>
          <p className="muted">
            If you live inside city limits, start with the city guide. The county page is for
            eligibility outside that city program.
          </p>
          <ul className="city-guide-list">
            {hub.cities.map((c) => (
              <li key={c.city_slug}>
                <Link href={`/${hub.state_slug}/${c.city_slug}#hhw`}>
                  {c.city} HHW program board
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {itemLinks.length ? (
        <section>
          <h2>Verified {leadCity.city} HHW item guides</h2>
          <ul className="city-guide-list">
            {itemLinks.map((p) =>
              p ? (
                <li key={p.item_slug}>
                  <Link href={cityItemHref(p)}>
                    {p.item_name} in {p.city}
                  </Link>
                </li>
              ) : null,
            )}
          </ul>
        </section>
      ) : null}

      <p>
        <Link href="/centers">Search drop-off sites by ZIP</Link>
        {" · "}
        <Link href="/counties">All county HHW hubs</Link>
        {" · "}
        <Link href="/guides/hhw-vs-bulk-vs-ewaste">HHW vs bulk vs e-waste</Link>
      </p>
    </div>
  );
}
