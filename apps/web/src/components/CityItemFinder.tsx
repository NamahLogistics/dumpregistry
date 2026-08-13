"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

type Guide = {
  item_slug: string;
  item_name: string;
  category: string;
  state_slug: string;
  city_slug: string;
  badge: string;
  href?: string;
};

export function CityItemFinder({
  city,
  guides,
  heading = "What do you need to dispose?",
  lead,
  hubHref,
  hubLabel,
}: {
  city: string;
  guides: Guide[];
  heading?: string;
  lead?: string;
  hubHref?: string;
  hubLabel?: string;
}) {
  const [q, setQ] = useState("");
  const categories = useMemo(
    () => [...new Set(guides.map((g) => g.category))].sort(),
    [guides],
  );
  const [cat, setCat] = useState<string | "all">("all");

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return guides
      .filter((g) => {
        if (cat !== "all" && g.category !== cat) return false;
        if (!needle) return true;
        return (
          g.item_name.toLowerCase().includes(needle) ||
          g.item_slug.includes(needle.replace(/\s+/g, "-")) ||
          g.category.toLowerCase().includes(needle)
        );
      })
      .sort((a, b) => a.item_name.localeCompare(b.item_name));
  }, [guides, q, cat]);

  if (!guides.length) return null;

  return (
    <section className="item-finder" aria-labelledby="item-finder-heading">
      <h2 id="item-finder-heading">{heading}</h2>
      <p className="item-finder-lead">
        {lead ??
          `All ${guides.length} verified guides for ${city}. Search or filter by category.`}
      </p>
      <label className="item-finder-search">
        <span className="sr-only">Search items</span>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search: mattress, lithium battery, paint…"
          autoComplete="off"
        />
      </label>
      <div className="item-finder-cats" role="list">
        <button
          type="button"
          className={cat === "all" ? "chip active" : "chip"}
          onClick={() => setCat("all")}
        >
          All ({guides.length})
        </button>
        {categories.map((c) => {
          const count = guides.filter((g) => g.category === c).length;
          return (
            <button
              key={c}
              type="button"
              className={cat === c ? "chip active" : "chip"}
              onClick={() => setCat(c)}
            >
              {c} ({count})
            </button>
          );
        })}
      </div>
      <p className="item-finder-count">
        Showing {filtered.length} of {guides.length}
      </p>
      <div className="hub-grid">
        {hubHref ? (
          <Link className="hub-link" href={hubHref}>
            {hubLabel ?? `${city} hub`}
            <span className="hub-link-meta">All city guides</span>
          </Link>
        ) : null}
        {filtered.map((g) => (
          <Link
            key={g.item_slug}
            className="hub-link"
            href={g.href ?? `/${g.state_slug}/${g.city_slug}/dispose/${g.item_slug}`}
          >
            {g.item_name}
            <span className="hub-link-meta">{g.category}</span>
          </Link>
        ))}
      </div>
      {!filtered.length ? (
        <p className="item-finder-empty">
          No match in {city} yet. Try another word, or browse categories above.
        </p>
      ) : null}
    </section>
  );
}
