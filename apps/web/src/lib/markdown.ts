import { readFileSync, readdirSync, existsSync } from "node:fs";
import path from "node:path";
import { contentRoot } from "./paths";

export type GuideMeta = {
  slug: string;
  title: string;
  description: string;
  date: string;
  body: string;
};

function parseFrontmatter(raw: string): { meta: Record<string, string>; body: string } {
  if (!raw.startsWith("---\n")) return { meta: {}, body: raw };
  const end = raw.indexOf("\n---\n", 4);
  if (end < 0) return { meta: {}, body: raw };
  const fm = raw.slice(4, end);
  const body = raw.slice(end + 5);
  const meta: Record<string, string> = {};
  for (const line of fm.split("\n")) {
    const i = line.indexOf(":");
    if (i < 0) continue;
    meta[line.slice(0, i).trim()] = line.slice(i + 1).trim().replace(/^["']|["']$/g, "");
  }
  return { meta, body };
}

export function listGuides(): GuideMeta[] {
  const dir = path.join(contentRoot(), "guides");
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((f) => f.endsWith(".md"))
    .map((file) => {
      const slug = file.replace(/\.md$/, "");
      const raw = readFileSync(path.join(dir, file), "utf8");
      const { meta, body } = parseFrontmatter(raw);
      return {
        slug,
        title: meta.title || slug,
        description: meta.description || "",
        date: meta.date || "",
        body,
      };
    })
    .sort((a, b) => (b.date || "").localeCompare(a.date || ""));
}

export function getGuide(slug: string): GuideMeta | null {
  return listGuides().find((g) => g.slug === slug) ?? null;
}

/** Minimal markdown → React-friendly blocks (headings, lists, paragraphs, links as text). */
export function markdownBlocks(md: string): Array<
  | { type: "h1" | "h2" | "h3" | "p"; text: string }
  | { type: "ul"; items: string[] }
> {
  const blocks: Array<
    | { type: "h1" | "h2" | "h3" | "p"; text: string }
    | { type: "ul"; items: string[] }
  > = [];
  for (const block of md.split(/\n\n+/).filter(Boolean)) {
    if (block.startsWith("# ")) blocks.push({ type: "h1", text: block.replace(/^#\s+/, "") });
    else if (block.startsWith("## ")) blocks.push({ type: "h2", text: block.replace(/^##\s+/, "") });
    else if (block.startsWith("### ")) blocks.push({ type: "h3", text: block.replace(/^###\s+/, "") });
    else if (block.split("\n").every((l) => l.startsWith("- "))) {
      blocks.push({ type: "ul", items: block.split("\n").map((l) => l.replace(/^- /, "")) });
    } else blocks.push({ type: "p", text: block.replace(/\n/g, " ") });
  }
  return blocks;
}
