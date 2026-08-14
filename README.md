# DumpRegistry.org

Human-first disposal guidance for hard-to-trash items. California city guides ship first; nationwide coverage expands only with verified sources.

## Stack

- `apps/web` — Next.js App Router site (Cloudflare-ready via OpenNext later)
- `packages/db` — Drizzle + Postgres schema/seed
- `data/` — items, geo, sourced rules, resolved pages
- `scripts/` — ZIP download, page resolve, sitemaps, IndexNow, freshness flags

## Quick start

```bash
pnpm install
python3 scripts/resolve_pages.py
python3 scripts/generate_sitemaps.py
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000).

## Data pipeline

```bash
python3 scripts/download_zips.py   # optional network refresh
python3 scripts/import_rules.py
python3 scripts/resolve_pages.py
python3 scripts/generate_sitemaps.py
python3 scripts/ping_indexnow.py   # dry-run by default
python3 scripts/smoke_check.py
```

## Postgres (optional)

```bash
docker compose up -d
export DATABASE_URL=postgres://postgres:postgres@localhost:5432/dumpregistry
pnpm db:generate
pnpm db:migrate
pnpm db:seed
```

The web app reads resolved JSON by default so local demos work without Postgres.

## Indexing policy

Only pages with sourced state/city rules are `indexable` and included in sitemaps. Thin defaults remain usable via the wizard with `noindex,follow`.

## Growth / measurement

See [docs/GROWTH.md](docs/GROWTH.md) for GA4, Google Search Console, and IndexNow setup (`NEXT_PUBLIC_GA_ID`, `NEXT_PUBLIC_GSC_VERIFICATION`, `INDEXNOW_KEY`).

```bash
pnpm data:sitemaps
pnpm data:indexnow        # dry-run
pnpm data:indexnow:live   # production ping
```

## Monetization

Set `NEXT_PUBLIC_ADS_PROVIDER=adsense` and `NEXT_PUBLIC_ADSENSE_CLIENT=ca-pub-…` (script + `ads.txt`). Pickup forms post to `/api/leads` (ZIP-matched, one hauler, Dodo prepaid packs). Partner apply is `/partners`. Webhook: `DODO_PAYMENTS_API_KEY`, `DODO_PAYMENTS_WEBHOOK_KEY`, `DODO_PAYMENTS_ENVIRONMENT`, `DODO_PRODUCT_ID_LEAD_PACK`.
