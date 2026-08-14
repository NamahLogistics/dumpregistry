import { adsEnabled, adsProvider } from "@/lib/ads";

/**
 * Reserved display slots. Auto ads do not use these — they stay empty until a
 * real `data-ad-slot` id exists. Never show dummy "AdSense placeholder" UI.
 */
export function AdSlot({ slot }: { slot: "anchor" | "inline" }) {
  const mode = adsProvider();
  if (!adsEnabled() || mode === "adsense") return null;

  return (
    <aside className={`ad-slot ad-${slot}`} aria-label="Advertisement" data-ad-provider={mode} data-ad-slot={slot} />
  );
}
