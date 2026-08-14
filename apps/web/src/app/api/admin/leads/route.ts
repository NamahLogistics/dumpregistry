import { NextResponse } from "next/server";
import { getSql } from "@/lib/db";
import { ensureMarketplaceSchema } from "@/lib/marketplace-schema";

function authorized(req: Request) {
  const token = process.env.ADMIN_TOKEN;
  if (!token) return false;
  return (req.headers.get("authorization") ?? "") === `Bearer ${token}`;
}

const STATUSES = ["new", "qualified", "routed", "unmatched", "closed", "spam"] as const;

export async function GET(req: Request) {
  if (!authorized(req)) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const db = getSql();
  if (!db) return NextResponse.json({ error: "DATABASE_URL required" }, { status: 503 });

  await ensureMarketplaceSchema(db);

  const rows = await db`
    SELECT id, city, state, zip, item_slug, name, email, phone, notes, status, partner_id, routed_at, created_at
    FROM lead_requests
    ORDER BY created_at DESC
    LIMIT 200
  `;
  return NextResponse.json({ leads: rows });
}

export async function PATCH(req: Request) {
  if (!authorized(req)) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const body = await req.json();
  const id = Number(body.id);
  const status = String(body.status ?? "");
  if (!id || !STATUSES.includes(status as (typeof STATUSES)[number])) {
    return NextResponse.json({ error: "Invalid payload" }, { status: 400 });
  }

  const db = getSql();
  if (!db) return NextResponse.json({ error: "DATABASE_URL required" }, { status: 503 });

  await db`UPDATE lead_requests SET status = ${status} WHERE id = ${id}`;
  return NextResponse.json({
    ok: true,
    id,
    status,
    note: "Status updated. Partner email and Dodo credits are not changed from this screen.",
  });
}
