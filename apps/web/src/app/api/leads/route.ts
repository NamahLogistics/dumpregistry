import { mkdirSync, appendFileSync } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";
import { getSql } from "@/lib/db";
import { dataRoot } from "@/lib/paths";

export async function POST(req: Request) {
  const body = await req.json();
  const name = String(body.name ?? "").trim();
  const email = String(body.email ?? "").trim();
  const city = String(body.city ?? "").trim();
  const state = String(body.state ?? "").trim();
  const phone = body.phone ? String(body.phone) : null;
  const notes = body.notes ? String(body.notes) : null;
  const itemSlug = body.itemSlug ? String(body.itemSlug) : null;

  if (!name || !email.includes("@") || !city || !state) {
    return NextResponse.json({ error: "Invalid lead" }, { status: 400 });
  }

  const db = getSql();
  if (db) {
    await db`
      INSERT INTO lead_requests (city, state, item_slug, name, email, phone, notes, status)
      VALUES (${city}, ${state}, ${itemSlug}, ${name}, ${email}, ${phone}, ${notes}, 'new')
    `;
    return NextResponse.json({ ok: true, storage: "neon" });
  }

  const dir = path.join(dataRoot(), "submissions");
  mkdirSync(dir, { recursive: true });
  appendFileSync(
    path.join(dir, "leads.jsonl"),
    `${JSON.stringify({
      createdAt: new Date().toISOString(),
      name,
      email,
      phone,
      notes,
      city,
      state,
      itemSlug,
      status: "new",
    })}\n`,
    "utf8",
  );
  return NextResponse.json({ ok: true, storage: "file" });
}
