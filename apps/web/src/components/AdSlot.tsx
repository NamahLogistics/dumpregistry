type Provider = "off" | "adsense" | "journey" | "mediavine";

function provider(): Provider {
  const value = (process.env.NEXT_PUBLIC_ADS_PROVIDER ?? "off").toLowerCase();
  if (value === "adsense" || value === "journey" || value === "mediavine") return value;
  return "off";
}

export function AdSlot({ slot }: { slot: "anchor" | "inline" }) {
  const mode = provider();
  if (mode === "off") return null;

  return (
    <aside className={`ad-slot ad-${slot}`} aria-label="Advertisement">
      <div className="ad-placeholder">
        {mode === "adsense" && slot === "anchor"
          ? "AdSense sticky anchor (env-enabled)"
          : mode === "adsense"
            ? "AdSense inline unit (env-enabled)"
            : mode === "journey"
              ? "Journey by Mediavine slot (env-enabled)"
              : "Mediavine slot (env-enabled)"}
      </div>
    </aside>
  );
}
