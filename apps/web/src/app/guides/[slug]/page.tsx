import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ContinueReading, pagesToContinueLinks } from "@/components/ContinueReading";
import { GUIDE_CITY_HUBS, GUIDE_DISPOSE_ITEM } from "@/lib/guide-links";
import { getGuide, listGuides, markdownBlocks } from "@/lib/markdown";
import { getCtrOverride, getMaterialCityGuides, getTopCoveredCities } from "@/lib/data";
import { pageMetadata } from "@/lib/seo";

type Props = { params: Promise<{ slug: string }> };

export async function generateStaticParams() {
  return listGuides().map((g) => ({ slug: g.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const guide = getGuide(slug);
  if (!guide) return { title: "Guide" };
  const path = `/guides/${guide.slug}`;
  const override = getCtrOverride(path);
  return pageMetadata({
    title: override?.title ?? guide.title,
    description: override?.description ?? guide.description,
    path,
  });
}

export default async function GuidePage({ params }: Props) {
  const { slug } = await params;
  const guide = getGuide(slug);
  if (!guide) notFound();
  const blocks = markdownBlocks(guide.body);

  return (
    <article className="shell page prose">
      <p className="eyebrow">
        <Link href="/guides">Guides</Link>
        {guide.date ? ` · ${guide.date}` : ""}
      </p>
      {blocks.map((b, i) => {
        if (b.type === "ul") {
          return (
            <ul key={i}>
              {b.items.map((item) => (
                <li key={item}>{renderInline(item)}</li>
              ))}
            </ul>
          );
        }
        if (b.type === "h1") return <h1 key={i}>{b.text}</h1>;
        if (b.type === "h2") return <h2 key={i}>{b.text}</h2>;
        if (b.type === "h3") return <h3 key={i}>{b.text}</h3>;
        return <p key={i}>{renderInline(b.text)}</p>;
      })}
      {GUIDE_CITY_HUBS.has(guide.slug) ? (
        <ContinueReading
          heading="City dump, bulky & HHW hubs"
          lead="Verified local rules — not a generic /cities index."
          links={getTopCoveredCities(12).map((c) => ({
            href: `/${c.state_slug}/${c.city_slug}`,
            title: `${c.city}, ${c.state}`,
            meta: "Dump, bulky & HHW",
          }))}
        />
      ) : GUIDE_DISPOSE_ITEM[guide.slug] ? (
        <ContinueReading
          heading="City-sourced guides"
          lead="Official program links we verified — pick the metro you are actually in."
          links={pagesToContinueLinks(
            getMaterialCityGuides(GUIDE_DISPOSE_ITEM[guide.slug], 12),
            "city",
          )}
        />
      ) : null}
      <p>
        <Link href="/cities">Browse verified cities</Link>
        {" · "}
        <Link href="/centers">Find drop-off centers</Link>
        {" · "}
        <Link href="/materials">Materials encyclopedia</Link>
      </p>
    </article>
  );
}

function renderInline(text: string) {
  // Support [label](/path) links only — keeps renderer tiny and safe.
  const parts = text.split(/(\[[^\]]+\]\([^)]+\))/g);
  return parts.map((part, i) => {
    const m = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
    if (!m) return <span key={i}>{part}</span>;
    const href = m[2];
    if (href.startsWith("http")) {
      return (
        <a key={i} href={href} target="_blank" rel="noopener noreferrer">
          {m[1]}
        </a>
      );
    }
    return (
      <Link key={i} href={href}>
        {m[1]}
      </Link>
    );
  });
}
