import type { DisposalPage } from "@/lib/types";

export const TITLE_MAX = 60;
export const DESC_MAX = 155;

export type SnippetOverride = { title?: string; description?: string };

export function clipAtWord(text: string, max: number): string {
  const clean = text.replace(/\s+/g, " ").trim();
  if (clean.length <= max) return clean;
  const slice = clean.slice(0, max);
  const sp = slice.lastIndexOf(" ");
  const cut = (sp >= Math.floor(max * 0.55) ? slice.slice(0, sp) : slice)
    .replace(/[,:;–—\-/]+$/u, "")
    .trim();
  return cut;
}

export function clipMetaDescription(text: string, max = DESC_MAX): string {
  return clipAtWord(text, max);
}

export function titleCaseSlug(slug: string): string {
  const small = new Set(["of", "the", "and"]);
  return slug
    .split("-")
    .map((w, i) => {
      if (i > 0 && small.has(w)) return w;
      return w.charAt(0).toUpperCase() + w.slice(1);
    })
    .join(" ");
}

/** Prefer a real sentence; never cut mid-word. */
export function leadFromAnswer(answer: string, max = 140): string {
  const clean = answer.replace(/\s+/g, " ").trim();
  const re = /[.!?](?=\s+[A-Z0-9]|$)/g;
  let chosen = -1;
  let m: RegExpExecArray | null;
  while ((m = re.exec(clean))) {
    const end = m.index + 1;
    if (end >= 35 && end <= max) {
      chosen = end;
      if (end >= 90) break;
    }
    if (end > max) break;
  }
  if (chosen >= 35) return clean.slice(0, chosen).trim();
  return clipAtWord(clean, max);
}

function verifiedBit(iso: string | null | undefined): string {
  if (!iso) return "";
  const day = iso.slice(0, 10);
  const d = new Date(`${day}T00:00:00Z`);
  if (Number.isNaN(d.getTime())) return "";
  const mon = d.toLocaleString("en-US", { month: "short", timeZone: "UTC" });
  return `Verified ${mon} ${d.getUTCFullYear()}.`;
}

function saysFree(fee: string): boolean {
  const t = fee.toLowerCase();
  if (/^not\b|not typical free|not a (typical )?free|not free\b/.test(t)) return false;
  if (/^free\b/.test(t)) return true;
  return /\bfree for (eligible )?(city |county )?residents?\b/.test(t);
}

function noActiveHhw(blob: string): boolean {
  return /suspended|no (active |public )?hhw|no permanent/.test(blob);
}

/** One short SERP hook from verified fields — never invents fees. */
export function titleHook(
  page: Pick<
    DisposalPage,
    "answer" | "category" | "common_disposal_fee" | "is_curbside_allowed" | "nearest_facility_type"
  >,
): string | null {
  const fee = (page.common_disposal_fee || "").trim();
  const fac = (page.nearest_facility_type || "").trim();
  const blob = `${fee} ${fac} ${page.answer || ""}`.toLowerCase();

  if (noActiveHhw(blob) && /events?-only|collection event/.test(blob)) {
    return "events only";
  }
  if (/events?-only/.test(blob)) return "events only";
  if (/\bappointment\b|\bappt\b/.test(blob) && !/no appointment/.test(blob) && !/on-demand/.test(blob)) {
    return "appointment required";
  }
  const dollar = fee.match(/\$\d+(?:\.\d+)?/);
  if (dollar) return `${dollar[0]} fee`;
  if (saysFree(fee)) return "free drop-off";
  const mentionsCurbside = /curbside|bulk collection|bulky pickup|heavy.?trash|junk waste/.test(blob);
  const selfHaulOnly = /self-haul/.test(blob) && !mentionsCurbside;
  if (page.is_curbside_allowed && page.category === "Bulky" && mentionsCurbside && !selfHaulOnly) {
    return "bulky pickup";
  }
  if (page.is_curbside_allowed && mentionsCurbside && !selfHaulOnly) return "curbside options";
  if (noActiveHhw(blob)) return null;
  if (page.category === "Hazardous" || /\bhhw\b|household hazardous/.test(blob)) {
    return "HHW drop-off";
  }
  if (page.category === "Electronics") return "e-waste drop-off";
  return null;
}

export function disposeTitle(
  page: Pick<
    DisposalPage,
    | "item_name"
    | "city"
    | "state"
    | "answer"
    | "category"
    | "common_disposal_fee"
    | "is_curbside_allowed"
    | "nearest_facility_type"
  >,
  override?: string,
): string {
  if (override) return clipAtWord(override, TITLE_MAX);
  const loc = `${page.city}, ${page.state}`;
  const core = `${page.item_name} disposal in ${loc}`;
  const hook = titleHook(page);
  if (hook) {
    const withHook = `${page.item_name} disposal in ${loc} — ${hook}`;
    if (withHook.length <= TITLE_MAX) return withHook;
  }
  if (core.length <= TITLE_MAX) return core;
  const compact = `Dispose of ${page.item_name} in ${loc}`;
  if (compact.length <= TITLE_MAX) return compact;
  return clipAtWord(`${page.item_name} in ${loc}`, TITLE_MAX);
}

export function disposeDescription(
  page: Pick<DisposalPage, "answer" | "city" | "item_name" | "last_verified_at">,
  override?: string,
): string {
  if (override) return clipMetaDescription(override);
  const lead = leadFromAnswer(page.answer || "", DESC_MAX);
  if (!/[.!?]$/.test(lead)) return clipMetaDescription(lead);
  const proof = verifiedBit(page.last_verified_at);
  if (proof && lead.length + 1 + proof.length <= DESC_MAX) return `${lead} ${proof}`;
  return lead;
}

export function cityHubTitle(city: string, state: string): string {
  const core = `${city}, ${state} disposal guides`;
  const hooked = `${core} — bulky, HHW & e-waste`;
  return hooked.length <= TITLE_MAX ? hooked : core;
}

export function cityHubDescription(city: string, state: string, guideCount: number): string {
  const n = guideCount > 0 ? `${guideCount} verified` : "Verified";
  return clipMetaDescription(
    `${n} item guides for ${city}, ${state} — bulky pickup, HHW, e-waste, and appliances, with official sources.`,
  );
}

export function stateHubTitle(stateSlug: string): string {
  return `${titleCaseSlug(stateSlug)} city disposal guides`;
}

export function stateHubDescription(stateSlug: string, cityCount: number): string {
  const name = titleCaseSlug(stateSlug);
  const n = cityCount > 0 ? `${cityCount} cities` : "cities";
  return clipMetaDescription(
    `Verified bulky, HHW, and e-waste rules for ${n} in ${name} — city-sourced drop-off and pickup guides.`,
  );
}
