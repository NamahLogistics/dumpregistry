import type { Metadata } from "next";
import { readFileSync } from "node:fs";
import path from "node:path";
import { contentRoot } from "@/lib/paths";

import { pageMetadata } from "@/lib/seo";

export const metadata: Metadata = pageMetadata({
  title: "How DumpRegistry verifies disposal rules",
  description:
    "City-sourced only: official program pages, hard facilities, verification dates, and what we refuse to publish.",
  path: "/methodology",
});

export default function MethodologyPage() {
  const mdPath = path.join(contentRoot(), "methodology.md");
  let body = "";
  try {
    body = readFileSync(mdPath, "utf8");
  } catch {
    body = "Methodology file missing.";
  }
  const paragraphs = body.split(/\n\n+/).filter(Boolean);

  return (
    <article className="shell page prose">
      {paragraphs.map((block, i) => {
        if (block.startsWith("# ")) return <h1 key={i}>{block.replace(/^#\s+/, "")}</h1>;
        if (block.startsWith("## ")) return <h2 key={i}>{block.replace(/^##\s+/, "")}</h2>;
        if (block.startsWith("- ")) {
          return (
            <ul key={i}>
              {block.split("\n").map((line) => (
                <li key={line}>{line.replace(/^- /, "")}</li>
              ))}
            </ul>
          );
        }
        return <p key={i}>{block}</p>;
      })}
    </article>
  );
}
