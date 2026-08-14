import { NextResponse } from "next/server";
import { getSql } from "@/lib/db";
import { ensureMarketplaceSchema } from "@/lib/marketplace-schema";

function authorized(req: Request) {
  const token = process.env.ADMIN_TOKEN;
  if (!token) return false;
  return (req.headers.get("authorization") ?? "") === `Bearer ${token}`;
}

const STATUSES = ["active", "paused", "paused_payment", "rejected"] as const;

export async function GET(req: Request) {
  if (!authorized(req)) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const db = getSql();
  if (!db) return NextResponse.json({ error: "DATABASE_URL required" }, { status: 503 });
  await ensureMarketplaceSchema(db);

  const rows = await db`
    SELECT id, company, contact_name, email, phone, cities, services, notes, plan, status, created_at,
           shop_zip, coverage_zips, radius_miles, dodo_customer_id, lead_credits, leads_routed_count
    FROM partner_applications
    ORDER BY created_at DESC
    LIMIT 200
  `;
  return NextResponse.json({ partners: rows });
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
  await ensureMarketplaceSchema(db);

  const existing = await db`
    SELECT id FROM partner_applications WHERE id = ${id} LIMIT 1
  `;
  if (!existing.length) return NextResponse.json({ error: "Not found" }, { status: 404 });

  await db`UPDATE partner_applications SET status = ${status} WHERE id = ${id}`;
  return NextResponse.json({
    ok: true,
    id,
    status,
    note: "Override only. Onboarding and billing stay on Dodo + ZIP coverage.",
  });
}
