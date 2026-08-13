import Link from "next/link";
import { cityItemHref } from "@/lib/data";
import type { DisposalPage } from "@/lib/types";

type LinkItem = {
  href: string;
  title: string;
  meta?: string;
};

export function ContinueReading({
  heading,
  lead,
  links,
  id,
}: {
  heading: string;
  lead?: string;
  links: LinkItem[];
  id?: string;
}) {
  if (!links.length) return null;
  return (
    <section className="continue-block" aria-labelledby={id ?? undefined}>
      <div className="continue-head">
        <h2 id={id}>{heading}</h2>
        {lead ? <p>{lead}</p> : null}
      </div>
      <div className="continue-grid">
        {links.map((l) => (
          <Link key={l.href} className="continue-card" href={l.href}>
            <strong>{l.title}</strong>
            {l.meta ? <span>{l.meta}</span> : null}
            <em>Open guide</em>
          </Link>
        ))}
      </div>
    </section>
  );
}

export function pagesToContinueLinks(pages: DisposalPage[], mode: "item" | "city" = "item"): LinkItem[] {
  return pages.map((p) => ({
    href: cityItemHref(p),
    title: mode === "city" ? `${p.item_name} in ${p.city}` : p.item_name,
    meta: mode === "city" ? p.category : `in ${p.city} · ${p.category}`,
  }));
}
