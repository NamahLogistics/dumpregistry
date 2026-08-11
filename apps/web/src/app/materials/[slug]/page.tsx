import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  badgeLabel,
  getItem,
  getItems,
  getMaterialCityGuides,
  getMaterialGuideCount,
} from "@/lib/data";

type Props = { params: Promise<{ slug: string }> };

export async function generateStaticParams() {
  return getItems().map((i) => ({ slug: i.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const item = getItem(slug);
  if (!item) return { title: "Material" };
  return {
    title: `How to dispose of ${item.name}`,
    description: `${item.summary_default} See city-sourced program guides across the U.S.`,
  };
}

export default async function MaterialPage({ params }: Props) {
  const { slug } = await params;
  const item = getItem(slug);
  if (!item) notFound();

  const cities = getMaterialCityGuides(slug, 48);
  const count = getMaterialGuideCount(slug);

  return (
    <article className="shell page prose">
      <p className="eyebrow">
        <Link href="/materials">Materials</Link> · {item.category}
      </p>
      <h1>How to dispose of {item.name}</h1>
      <p>{item.summary_default}</p>

      <section>
        <h2>What usually applies</h2>
        <ul>
          <li>
            <strong>Handling:</strong> {badgeLabel(item.badge_default)}
          </li>
          <li>
            <strong>Hazard:</strong> {item.hazard_default}
          </li>
          <li>
            <strong>Typical fee band:</strong> {item.fee_band_default}
          </li>
          <li>
            <strong>Usual channel:</strong> {item.facility_type_default}
          </li>
          <li>
            <strong>Curbside by default?</strong> {item.curbside_default ? "Sometimes" : "Usually not in the regular cart"}
          </li>
        </ul>
        <p>
          Rules vary by city. Use a verified local guide below — or find drop-off sites on{" "}
          <Link href={`/centers?material=${item.slug}`}>Centers near you</Link>.
        </p>
      </section>

      <section>
        <h2>City-sourced guides ({count})</h2>
        <p>Each guide names the official program source and when we last verified it.</p>
        <ul className="city-guide-list">
          {cities.map((p) => (
            <li key={`${p.state_slug}-${p.city_slug}`}>
              <Link href={`/${p.state_slug}/${p.city_slug}/dispose/${p.item_slug}`}>
                {p.city}, {p.state}
              </Link>
            </li>
          ))}
        </ul>
        {count > cities.length ? (
          <p className="muted">Showing {cities.length} of {count} — open Cities for the full list.</p>
        ) : null}
      </section>
    </article>
  );
}
