import type { Metadata } from "next";
import { site } from "@/lib/site";
import { clipMetaDescription } from "@/lib/snippets";

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

/** Unique title/description plus matching OG/Twitter — layout OG no longer clobbers these. */
export function pageMetadata(opts: {
  title: string;
  description: string;
  path: string;
  index?: boolean;
  follow?: boolean;
}): Metadata {
  const description = clipMetaDescription(opts.description);
  const index = opts.index ?? true;
  const follow = opts.follow ?? true;
  return {
    title: opts.title,
    description,
    robots: { index, follow },
    ...canonicalMetadata(opts.path),
    openGraph: {
      title: opts.title,
      description,
      url: absoluteUrl(opts.path),
      siteName: site.name,
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: opts.title,
      description,
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
