import { mkdirSync, appendFileSync } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";
import { getSql } from "@/lib/db";
import { dataRoot } from "@/lib/paths";

type Body = {
  stateSlug?: string;
  citySlug?: string;
  itemSlug?: string;
  message?: string;
  sourceUrl?: string;
  email?: string;
};

function isAllowedUrl(url: string) {
  try {
    const u = new URL(url);
    if (!["http:", "https:"].includes(u.protocol)) return false;
    const host = u.hostname.toLowerCase();
    return host.endsWith(".gov") || host.endsWith(".org") || host.endsWith(".com");
  } catch {
    return false;
  }
}

export async function POST(req: Request) {
  const body = (await req.json()) as Body;
  const message = (body.message ?? "").trim();
  const sourceUrl = (body.sourceUrl ?? "").trim();
  const stateSlug = (body.stateSlug ?? "").trim();
  const citySlug = (body.citySlug ?? "").trim();
  const itemSlug = body.itemSlug ?? null;
  const email = body.email ?? null;

  if (message.length < 20 || message.length > 2000) {
    return NextResponse.json({ error: "Invalid message" }, { status: 400 });
  }
  if (!stateSlug || !citySlug || !isAllowedUrl(sourceUrl)) {
    return NextResponse.json({ error: "Invalid fields" }, { status: 400 });
  }

  const db = getSql();
  if (db) {
    await db`
      INSERT INTO user_submissions (state_slug, city_slug, item_slug, message, source_url, email, status)
      VALUES (${stateSlug}, ${citySlug}, ${itemSlug}, ${message}, ${sourceUrl}, ${email}, 'pending')
    `;
    return NextResponse.json({ ok: true, storage: "neon" });
  }

  const dir = path.join(dataRoot(), "submissions");
  mkdirSync(dir, { recursive: true });
  appendFileSync(
    path.join(dir, "updates.jsonl"),
    `${JSON.stringify({
      createdAt: new Date().toISOString(),
      stateSlug,
      citySlug,
      itemSlug,
      message,
      sourceUrl,
      email,
      status: "pending",
    })}\n`,
    "utf8",
  );
  return NextResponse.json({ ok: true, storage: "file" });
}
