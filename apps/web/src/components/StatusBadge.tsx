import { badgeLabel } from "@/lib/data";

export function StatusBadge({ badge }: { badge: string }) {
  const tone =
    badge === "BANNED_FROM_LANDFILLS"
      ? "badge-banned"
      : badge === "ACCEPTED_IN_BLUE_BIN"
        ? "badge-ok"
        : "badge-special";
  return <span className={`status-badge ${tone}`}>{badgeLabel(badge)}</span>;
}
