export type AdsProvider = "off" | "adsense" | "journey" | "mediavine";

/** Public AdSense publisher id — also used for site verification (meta + ads.txt). */
export const ADSENSE_PUB = "ca-pub-3690708569787606";

export function adsProvider(): AdsProvider {
  const value = (process.env.NEXT_PUBLIC_ADS_PROVIDER ?? "off").toLowerCase();
  if (value === "adsense" || value === "journey" || value === "mediavine") return value;
  return "off";
}

export function adsenseClient(): string | null {
  const client = process.env.NEXT_PUBLIC_ADSENSE_CLIENT?.trim();
  return client || ADSENSE_PUB;
}

export function adsEnabled(): boolean {
  const mode = adsProvider();
  if (mode === "adsense") return Boolean(adsenseClient());
  if (mode === "journey" || mode === "mediavine") {
    return Boolean(process.env.NEXT_PUBLIC_MEDIAVINE_SITE_ID?.trim());
  }
  return false;
}
