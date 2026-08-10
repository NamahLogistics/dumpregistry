import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { AdSlot } from "@/components/AdSlot";
import { CorrectionWidget } from "@/components/CorrectionWidget";
import { FaqSection, faqJsonLd, howToJsonLd } from "@/components/FaqSection";
import { LeadModule } from "@/components/LeadModule";
import { MapPlaceholder } from "@/components/MapPlaceholder";
import { SpecsTable } from "@/components/SpecsTable";
import { StatusBadge } from "@/components/StatusBadge";
import { getPage, getPages } from "@/lib/data";

type Props = {
  params: Promise<{ state: string; city: string; item: string }>;
};

export async function generateStaticParams() {
  return getPages().map((p) => ({
    state: p.state_slug,
    city: p.city_slug,
    item: p.item_slug,
  }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { state, city, item } = await params;
  const page = getPage(state, city, item);
  if (!page) return {};
  return {
    title: `How to Dispose of ${page.item_name} in ${page.city}, ${page.state}`,
    description: page.answer.slice(0, 155),
    robots: page.indexable ? { index: true, follow: true } : { index: false, follow: true },
  };
}

export default async function DisposeItemPage({ params }: Props) {
  const { state, city, item } = await params;
  const page = getPage(state, city, item);
  if (!page) notFound();

  const siblings = getPages()
    .filter((p) => p.state_slug === state && p.city_slug === city && p.indexable && p.item_slug !== item)
    .slice(0, 8);

  return (
    <div className="shell page">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd(page.faqs)) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(
            howToJsonLd(
              `How to dispose of ${page.item_name} in ${page.city}`,
              page.answer,
              page.steps,
            ),
          ),
        }}
      />

      <section className="answer-band">
        <StatusBadge badge={page.badge} />
        <h1>
          How to Dispose of {page.item_name} in {page.city}, {page.state}
        </h1>
        <p className="direct-answer">{page.answer}</p>
        <div className="meta-row">
          <span>Category: {page.category}</span>
          <span>
            Based on {page.rule_source_level}
            {page.source_name ? ` · ${page.source_name}` : ""}
          </span>
          {page.source_url ? (
            <a href={page.source_url} target="_blank" rel="noopener noreferrer">
              View source
            </a>
          ) : (
            <span>General guidance (not locally verified)</span>
          )}
        </div>
      </section>

      <section>
        <h2>Local specifics</h2>
        <SpecsTable page={page} />
      </section>

      <section>
        <h2>What to do today</h2>
        <ol className="steps">
          {page.steps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </section>

      <AdSlot slot="inline" />

      <MapPlaceholder
        lat={page.lat}
        lng={page.lng}
        city={page.city}
        facilities={page.facilities}
      />

      <FaqSection faqs={page.faqs} />

      <LeadModule city={page.city} state={page.state} itemSlug={page.item_slug} />

      <section>
        <h2>More in {page.city}</h2>
        <div className="hub-grid">
          <Link className="hub-link" href={`/${page.state_slug}/${page.city_slug}`}>
            {page.city} hub
          </Link>
          {siblings.map((s) => (
            <Link
              key={s.item_slug}
              className="hub-link"
              href={`/${s.state_slug}/${s.city_slug}/dispose/${s.item_slug}`}
            >
              {s.item_name}
            </Link>
          ))}
        </div>
      </section>

      <CorrectionWidget
        city={page.city}
        stateSlug={page.state_slug}
        citySlug={page.city_slug}
        itemSlug={page.item_slug}
      />
      <AdSlot slot="anchor" />
    </div>
  );
}
