import { mkdirSync, appendFileSync } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";
import { getSql } from "@/lib/db";
import { escapeHtml, opsInbox, sendEmail } from "@/lib/email";
import { dataRoot } from "@/lib/paths";

export async function POST(req: Request) {
  const body = await req.json();
  const company = String(body.company ?? "").trim();
  const contactName = String(body.contactName ?? "").trim();
  const email = String(body.email ?? "").trim();
  const phone = body.phone ? String(body.phone).trim() : null;
  const cities = String(body.cities ?? "").trim();
  const services = String(body.services ?? "").trim();
  const notes = body.notes ? String(body.notes).trim() : null;
  const plan = body.plan ? String(body.plan).trim() : "starter";

  if (!company || !contactName || !email.includes("@") || cities.length < 3 || services.length < 3) {
    return NextResponse.json({ error: "Invalid partner application" }, { status: 400 });
  }

  const db = getSql();
  if (db) {
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
    await db`ALTER TABLE partner_applications ADD COLUMN IF NOT EXISTS plan VARCHAR(40) DEFAULT 'starter'`;
    await db`
      INSERT INTO partner_applications (company, contact_name, email, phone, cities, services, notes, plan, status)
      VALUES (${company}, ${contactName}, ${email}, ${phone}, ${cities}, ${services}, ${notes}, ${plan}, 'pending')
    `;
  } else {
    const dir = path.join(dataRoot(), "submissions");
    mkdirSync(dir, { recursive: true });
    appendFileSync(
      path.join(dir, "partners.jsonl"),
      `${JSON.stringify({
        createdAt: new Date().toISOString(),
        company,
        contactName,
        email,
        phone,
        cities,
        services,
        notes,
        plan,
        status: "pending",
      })}\n`,
      "utf8",
    );
  }

  const site = process.env.NEXT_PUBLIC_SITE_URL ?? "https://www.dumpregistry.org";
  await sendEmail({
    to: email,
    subject: "DumpRegistry partner application received",
    html: `<p>Hi ${escapeHtml(contactName)},</p>
<p>We received your DumpRegistry partner application for <strong>${escapeHtml(company)}</strong>.</p>
<p><strong>Plan:</strong> ${escapeHtml(plan)}<br/>
<strong>Cities:</strong> ${escapeHtml(cities)}<br/>
<strong>Services:</strong> ${escapeHtml(services)}</p>
<p>No sales call needed — we’ll email next steps (sample lead format + pilot activation).</p>
<p><a href="${site}/partners">Partners page</a></p>`,
    text: `Hi ${contactName},\n\nWe received your partner application for ${company} (${plan}) covering ${cities}.\nWe’ll email next steps.\n`,
  });

  const ops = opsInbox();
  if (ops) {
    await sendEmail({
      to: ops,
      subject: `[Partner apply] ${company} — ${cities}`,
      replyTo: email,
      html: `<p>New partner application</p>
<ul>
<li>Company: ${escapeHtml(company)}</li>
<li>Contact: ${escapeHtml(contactName)}</li>
<li>Email: ${escapeHtml(email)}</li>
<li>Phone: ${escapeHtml(phone ?? "—")}</li>
<li>Plan: ${escapeHtml(plan)}</li>
<li>Cities: ${escapeHtml(cities)}</li>
<li>Services: ${escapeHtml(services)}</li>
<li>Notes: ${escapeHtml(notes ?? "—")}</li>
</ul>
<p>Activate in <a href="${site}/admin/partners">/admin/partners</a> when ready to receive leads.</p>`,
    });
  }

  return NextResponse.json({ ok: true, storage: db ? "neon" : "file" });
}
