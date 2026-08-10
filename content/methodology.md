# Methodology

DumpRegistry publishes disposal guidance only when we can point to a source, or we clearly label the page as general guidance and keep it out of search indexes.

## What we store

- Geography for city/ZIP hubs and distance context
- A catalog of high-intent hard-to-dispose items
- Sparse rules at state or city level with `source_url`, `source_name`, and `last_verified_at`
- Optional facility seeds for transfer/HHW orientation

## Inheritance

City rules override state rules. If neither exists, the item default is shown inside the wizard and utility pages with `noindex`, so search engines are not asked to rank thin placeholders.

## Automation disclosure

We use scripts to cross-reference geography with items and to generate sitemaps. The factual answer on each indexable page comes from reviewed rule records, not from unattended synonym spinning.

## Corrections

Anyone can suggest an update with an official URL. Submissions enter an editorial queue. We do not silently invent fees or bans.

## Freshness

A twice-yearly job flags major city portal pages when fee/ban language appears, marking related rows for review. We never fake “updated today” dates.
