import { mkdirSync, appendFileSync } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";
import { getSql } from "@/lib/db";
import { escapeHtml, opsInbox, sendEmail } from "@/lib/email";
import { dataRoot } from "@/lib/paths";

async function notifyLead(opts: {
  name: string;
  email: string;
  city: string;
  state: string;
  phone: string | null;
  notes: string | null;
  itemSlug: string | null;
}) {
  const site = process.env.NEXT_PUBLIC_SITE_URL ?? "https://www.dumpregistry.org";
  const item = opts.itemSlug ?? "pickup";

  await sendEmail({
    to: opts.email,
    subject: `We received your ${opts.city} pickup request`,
    html: `<p>Hi ${escapeHtml(opts.name)},</p>
<p>Thanks — we received your pickup request for <strong>${escapeHtml(item)}</strong> in ${escapeHtml(opts.city)}, ${escapeHtml(opts.state)}.</p>
<p>If a local hauler partner is available, they may contact you about options. This is separate from the free disposal guide on DumpRegistry.</p>
<p><a href="${site}">DumpRegistry</a></p>`,
    text: `Hi ${opts.name},\n\nWe received your pickup request for ${item} in ${opts.city}, ${opts.state}. A hauler partner may follow up if available.\n`,
  });

  const ops = opsInbox();
  if (ops) {
    await sendEmail({
      to: ops,
      subject: `[Lead] ${opts.city} — ${item}`,
      replyTo: opts.email,
      html: `<p>New consumer lead</p>
<ul>
<li>City: ${escapeHtml(opts.city)}, ${escapeHtml(opts.state)}</li>
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
    const matched = partners.filter((p) => {
      const hay = String(p.cities ?? "").toLowerCase();
      return hay.includes(opts.city.toLowerCase()) || hay.includes("all cities");
    });

    for (const p of matched) {
      await sendEmail({
        to: String(p.email),
        subject: `DumpRegistry lead: ${opts.city} — ${item}`,
        replyTo: ops ?? undefined,
        html: `<p>Hi ${escapeHtml(String(p.contact_name ?? p.company))},</p>
<p>New qualified pickup lead in <strong>${escapeHtml(opts.city)}</strong>:</p>
<ul>
<li>Item: ${escapeHtml(item)}</li>
<li>Name: ${escapeHtml(opts.name)}</li>
<li>Email: ${escapeHtml(opts.email)}</li>
<li>Phone: ${escapeHtml(opts.phone ?? "—")}</li>
<li>Notes: ${escapeHtml(opts.notes ?? "—")}</li>
</ul>
<p>Reply to the customer directly to quote. Questions → partners inbox.</p>`,
        text: `New lead in ${opts.city} for ${item}.\n${opts.name} / ${opts.email} / ${opts.phone ?? ""}\n${opts.notes ?? ""}\n`,
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
        itemSlug,
        status: "new",
      })}\n`,
      "utf8",
    );
  }

  // Fire-and-forget style: await so serverless doesn't freeze mid-send
  await notifyLead({ name, email, city, state, phone, notes, itemSlug });

  return NextResponse.json({ ok: true, storage: db ? "neon" : "file" });
}
