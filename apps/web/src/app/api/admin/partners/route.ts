import { NextResponse } from "next/server";
import { getSql } from "@/lib/db";
import { escapeHtml, sendEmail } from "@/lib/email";

function authorized(req: Request) {
  const token = process.env.ADMIN_TOKEN;
  if (!token) return false;
  return (req.headers.get("authorization") ?? "") === `Bearer ${token}`;
}

const STATUSES = ["pending", "active", "paused", "rejected"] as const;

export async function GET(req: Request) {
  if (!authorized(req)) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const db = getSql();
  if (!db) return NextResponse.json({ error: "DATABASE_URL required" }, { status: 503 });

  await db`
    CREATE TABLE IF NOT EXISTS partner_applications (
      id SERIAL PRIMARY KEY,
      company VARCHAR(160) NOT NULL,
      contact_name VARCHAR(120) NOT NULL,
      email VARCHAR(200) NOT NULL,
      phone VARCHAR(40),
      cities TEXT NOT NULL,
      services TEXT NOT NULL,
      notes TEXT,
      plan VARCHAR(40) DEFAULT 'starter',
      status VARCHAR(40) NOT NULL DEFAULT 'pending',
      created_at TIMESTAMPTZ DEFAULT NOW()
    )
  `;

  const rows = await db`
    SELECT id, company, contact_name, email, phone, cities, services, notes, plan, status, created_at
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

  const existing = await db`
    SELECT id, email, contact_name, company, cities, status
    FROM partner_applications WHERE id = ${id} LIMIT 1
  `;
  if (!existing.length) return NextResponse.json({ error: "Not found" }, { status: 404 });

  await db`UPDATE partner_applications SET status = ${status} WHERE id = ${id}`;

  const row = existing[0];
  if (status === "active" && row.status !== "active") {
    const site = process.env.NEXT_PUBLIC_SITE_URL ?? "https://www.dumpregistry.org";
    await sendEmail({
      to: String(row.email),
      subject: "You’re active on DumpRegistry leads",
      html: `<p>Hi ${escapeHtml(String(row.contact_name))},</p>
<p><strong>${escapeHtml(String(row.company))}</strong> is now <strong>active</strong> for leads in: ${escapeHtml(String(row.cities))}.</p>
<p>When a resident requests pickup in your cities, we’ll email you the lead details.</p>
<p><a href="${site}/partners">Partners info</a></p>`,
    });
  }

  return NextResponse.json({ ok: true, id, status });
}
