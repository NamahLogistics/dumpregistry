/**
 * Ads render only when a real publisher id is configured.
 * Never show dummy "AdSense placeholder" UI.
 */
type Provider = "off" | "adsense" | "journey" | "mediavine";

function provider(): Provider {
  const value = (process.env.NEXT_PUBLIC_ADS_PROVIDER ?? "off").toLowerCase();
  if (value === "adsense" || value === "journey" || value === "mediavine") return value;
  return "off";
}

function hasPublisherConfig(mode: Provider) {
  if (mode === "adsense") return Boolean(process.env.NEXT_PUBLIC_ADSENSE_CLIENT);
  if (mode === "journey" || mode === "mediavine") {
    return Boolean(process.env.NEXT_PUBLIC_MEDIAVINE_SITE_ID);
  }
  return false;
}

export function AdSlot({ slot }: { slot: "anchor" | "inline" }) {
  const mode = provider();
  if (mode === "off" || !hasPublisherConfig(mode)) return null;

  // Real network scripts are injected by the publisher integration when IDs exist.
  return (
    <aside className={`ad-slot ad-${slot}`} aria-label="Advertisement" data-ad-provider={mode} data-ad-slot={slot} />
  );
}
