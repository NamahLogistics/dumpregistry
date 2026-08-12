import type { Metadata } from "next";
import { site } from "@/lib/site";

export function absoluteUrl(path: string): string {
  if (!path || path === "/") return site.url;
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${site.url}${p}`;
}

export function canonicalMetadata(path: string): Pick<Metadata, "alternates"> {
  return {
    alternates: {
      canonical: absoluteUrl(path),
    },
  };
}

export type Crumb = { name: string; path: string };

export function breadcrumbJsonLd(crumbs: Crumb[]) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: crumbs.map((c, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: c.name,
      item: absoluteUrl(c.path),
    })),
  };
}

/** Stable public slug for a facility detail page. */
export function facilitySlug(f: {
  city_slug: string;
  name: string;
  address?: string | null;
}): string {
  const raw = `${f.city_slug}-${f.name}-${f.address || ""}`
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 96);
  return raw || `${f.city_slug}-facility`;
}
