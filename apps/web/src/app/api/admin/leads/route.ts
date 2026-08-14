import { NextResponse } from "next/server";
import { getSql } from "@/lib/db";

function authorized(req: Request) {
  const token = process.env.ADMIN_TOKEN;
  if (!token) return false;
  return (req.headers.get("authorization") ?? "") === `Bearer ${token}`;
}

const STATUSES = ["new", "qualified", "routed", "closed", "spam"] as const;

export async function GET(req: Request) {
  if (!authorized(req)) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const db = getSql();
  if (!db) return NextResponse.json({ error: "DATABASE_URL required" }, { status: 503 });

  await db`ALTER TABLE lead_requests ADD COLUMN IF NOT EXISTS zip VARCHAR(16)`;

  const rows = await db`
    SELECT id, city, state, zip, item_slug, name, email, phone, notes, status, created_at
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
    note: "Lead status updated. Routing to partners is manual in v1 — never auto-sell without review.",
  });
}
