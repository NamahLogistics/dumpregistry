# Growth setup — path to 1M sessions/month

Operational checklist for measurement and indexation. Code hooks ship with env vars; accounts are created once in vendor consoles.

## 1. Google Analytics 4

**Live property (created 2026-08-12):**

| Field | Value |
|-------|--------|
| Account | DumpRegistry (`404390361`) |
| Property | DumpRegistry (`549559344`) |
| Web stream | DumpRegistry Web (`15422956726`) |
| Measurement ID | `G-KCR1N0X09L` |

- Vercel env: `NEXT_PUBLIC_GA_ID=G-KCR1N0X09L` (Production / Preview / Development)
- Tag loads via `apps/web/src/components/Analytics.tsx`
- Key events: `generate_lead` (custom, $1), plus lead-objective defaults `qualify_lead`, `close_convert_lead`, `purchase`
- Client fires `generate_lead` (pickup + partner forms) and `wizard_complete` via `apps/web/src/lib/analytics.ts`
- Default audiences: All Users, Purchasers

Vercel Analytics is enabled by default (no env required).

## 2. Google Search Console

**Live (2026-08-12):** URL-prefix property `https://www.dumpregistry.org/` — ownership auto-verified.

- Sitemap submitted: `https://www.dumpregistry.org/sitemap.xml` (Success; also `/sitemaps/sitemap-001.xml`)
- Optional: set `NEXT_PUBLIC_GSC_VERIFICATION` if you want an HTML meta tag as a second verification method
- Optional: GA4 Admin → Product links → Search Console links (link this property)

## 3. IndexNow (Bing / Yandex)

1. Key file is published at `https://www.dumpregistry.org/<INDEXNOW_KEY>.txt`
2. Set Vercel / CI env:
   - `INDEXNOW_KEY=<same key as filename>`
   - `INDEXNOW_DRY_RUN=0` for live pings
3. After each content publish:

```bash
INDEXNOW_DRY_RUN=0 pnpm data:indexnow
```

Default without env is dry-run (safe for local).

## 4. Weekly GSC loop (Phase 4)

- Queries with impressions + low CTR → rewrite titles/descriptions in `data/seo/ctr_overrides.json` (pathname → `{ title, description }`). Dispose pages pick these up at build time.
- Default snippets are generated in `apps/web/src/lib/snippets.ts` from verified city/item fields (no invented fees).
- Pages on page 2 → expand internal links from materials/hubs
- Soft-duplicate ZIP hubs → `noindex` if they cannibalize city pages
