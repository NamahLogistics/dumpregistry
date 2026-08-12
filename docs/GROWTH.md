# Growth setup — path to 1M sessions/month

Operational checklist for measurement and indexation. Code hooks ship with env vars; accounts are created once in vendor consoles.

## 1. Google Analytics 4

1. Create a GA4 property for `www.dumpregistry.org`.
2. Copy the Measurement ID (`G-XXXXXXXX`).
3. Set Vercel env: `NEXT_PUBLIC_GA_ID=G-XXXXXXXX`
4. Redeploy. Events load via `apps/web/src/components/Analytics.tsx`.

Vercel Analytics is enabled by default (no env required).

## 2. Google Search Console

1. Add property `https://www.dumpregistry.org`.
2. Choose HTML tag verification; copy the `content=` token.
3. Set Vercel env: `NEXT_PUBLIC_GSC_VERIFICATION=<token>`
4. Redeploy, complete verification in GSC.
5. Submit sitemap: `https://www.dumpregistry.org/sitemap.xml`

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

- Queries with impressions + low CTR → rewrite titles/descriptions
- Pages on page 2 → expand internal links from materials/hubs
- Soft-duplicate ZIP hubs → `noindex` if they cannibalize city pages
