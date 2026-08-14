import { mkdirSync, appendFileSync } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";
import { getSql } from "@/lib/db";
import { escapeHtml, opsInbox, sendEmail } from "@/lib/email";
import { dataRoot } from "@/lib/paths";

function partnerCovers(citiesField: string, city: string, state: string) {
  const hay = citiesField.toLowerCase();
  if (/(all cities|any city|nationwide|entire us|united states|all metros|all states)/i.test(hay)) {
    return true;
  }
  if (city && hay.includes(city.toLowerCase())) return true;
  if (state.length >= 2 && hay.includes(state.toLowerCase())) return true;
  return false;
}

function normalizeZip(raw: unknown) {
  const digits = String(raw ?? "").replace(/\D/g, "");
  if (digits.length < 5) return null;
  return digits.slice(0, 5);
}

async function notifyLead(opts: {
  name: string;
  email: string;
  city: string;
  state: string;
  zip: string | null;
  phone: string | null;
  notes: string | null;
  itemSlug: string | null;
}) {
  const site = process.env.NEXT_PUBLIC_SITE_URL ?? "https://www.dumpregistry.org";
  const item = opts.itemSlug ?? "pickup";
  const where = opts.zip
    ? `${opts.city}, ${opts.state} ${opts.zip}`
    : `${opts.city}, ${opts.state}`;

  await sendEmail({
    to: opts.email,
    subject: `We received your ${opts.city} pickup request`,
    html: `<p>Hi ${escapeHtml(opts.name)},</p>
<p>Thanks — we received your pickup request for <strong>${escapeHtml(item)}</strong> in ${escapeHtml(where)}.</p>
<p>If a hauler in our network covers your area, they may call with a quote. This is separate from the free disposal guide on DumpRegistry. You pay the hauler, not us.</p>
<p><a href="${site}">DumpRegistry</a></p>`,
    text: `Hi ${opts.name},\n\nWe received your pickup request for ${item} in ${where}. A hauler may follow up if they cover your area.\n`,
  });

  const ops = opsInbox();
  if (ops) {
    await sendEmail({
      to: ops,
      subject: `[Lead] ${opts.city} — ${item}`,
      replyTo: opts.email,
      html: `<p>New consumer lead</p>
<ul>
<li>Where: ${escapeHtml(where)}</li>
<li>Item: ${escapeHtml(item)}</li>
<li>Name: ${escapeHtml(opts.name)}</li>
<li>Email: ${escapeHtml(opts.email)}</li>
<li>Phone: ${escapeHtml(opts.phone ?? "—")}</li>
<li>Notes: ${escapeHtml(opts.notes ?? "—")}</li>
</ul>
<p>Route in <a href="${site}/admin/leads">/admin/leads</a></p>`,
    });
  }

  const db = getSql();
  if (!db) return;

  try {
    const partners = await db`
      SELECT email, company, contact_name, cities
      FROM partner_applications
      WHERE status = 'active'
      LIMIT 100
    `;
    const matched = partners.filter((p) => partnerCovers(String(p.cities ?? ""), opts.city, opts.state));

    for (const p of matched) {
      await sendEmail({
        to: String(p.email),
        subject: `DumpRegistry lead: ${opts.city} — ${item}`,
        replyTo: ops ?? undefined,
        html: `<p>Hi ${escapeHtml(String(p.contact_name ?? p.company))},</p>
<p>New pickup lead in <strong>${escapeHtml(where)}</strong>:</p>
<ul>
<li>Item: ${escapeHtml(item)}</li>
<li>Name: ${escapeHtml(opts.name)}</li>
<li>Email: ${escapeHtml(opts.email)}</li>
<li>Phone: ${escapeHtml(opts.phone ?? "—")}</li>
<li>Notes: ${escapeHtml(opts.notes ?? "—")}</li>
</ul>
<p>Reply to the customer directly to quote.</p>`,
        text: `New lead in ${where} for ${item}.\n${opts.name} / ${opts.email} / ${opts.phone ?? ""}\n${opts.notes ?? ""}\n`,
      });
    }
  } catch (err) {
    console.error("[leads] partner notify failed", err);
  }
}

export async function POST(req: Request) {
  const body = await req.json();
  const name = String(body.name ?? "").trim();
  const email = String(body.email ?? "").trim();
  const city = String(body.city ?? "").trim();
  const state = String(body.state ?? "").trim();
  const zip = normalizeZip(body.zip);
  const phone = body.phone ? String(body.phone).trim() : "";
  const notes = body.notes ? String(body.notes) : null;
  const itemSlug = body.itemSlug ? String(body.itemSlug) : null;

  if (!name || !email.includes("@") || !city || !state || !zip || phone.replace(/\D/g, "").length < 7) {
    return NextResponse.json({ error: "Invalid lead" }, { status: 400 });
  }

  const db = getSql();
  if (db) {
    await db`ALTER TABLE lead_requests ADD COLUMN IF NOT EXISTS zip VARCHAR(16)`;
    await db`
      INSERT INTO lead_requests (city, state, zip, item_slug, name, email, phone, notes, status)
      VALUES (${city}, ${state}, ${zip}, ${itemSlug}, ${name}, ${email}, ${phone}, ${notes}, 'new')
    `;
  } else {
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
        zip,
        itemSlug,
        status: "new",
      })}\n`,
      "utf8",
    );
  }

  await notifyLead({ name, email, city, state, zip, phone, notes, itemSlug });

  return NextResponse.json({ ok: true, storage: db ? "neon" : "file" });
}
