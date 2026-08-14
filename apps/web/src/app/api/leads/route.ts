import { mkdirSync, appendFileSync } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";
import { normalizeZip } from "@/lib/coverage";
import { getSql } from "@/lib/db";
import { escapeHtml, opsInbox, sendEmail } from "@/lib/email";
import { ensureMarketplaceSchema } from "@/lib/marketplace-schema";
import { maybePauseIfEmpty, pickPartnerForZip } from "@/lib/partner-billing";
import { dataRoot } from "@/lib/paths";
import { siteUrl } from "@/lib/dodo";

async function notifyResident(opts: {
  name: string;
  email: string;
  city: string;
  state: string;
  zip: string;
  itemSlug: string | null;
  routed: boolean;
}) {
  const where = `${opts.city}, ${opts.state} ${opts.zip}`;
  const item = opts.itemSlug ?? "pickup";
  await sendEmail({
    to: opts.email,
    subject: opts.routed
      ? `We sent your ${opts.city} pickup request to a local hauler`
      : `We received your ${opts.city} pickup request`,
    html: opts.routed
      ? `<p>Hi ${escapeHtml(opts.name)},</p>
<p>We received your pickup request for <strong>${escapeHtml(item)}</strong> in ${escapeHtml(where)} and sent it to one hauler who listed that ZIP.</p>
<p>They may call with a quote. You pay them, not DumpRegistry. The free disposal guide stays free.</p>
<p><a href="${siteUrl()}">DumpRegistry</a></p>`
      : `<p>Hi ${escapeHtml(opts.name)},</p>
<p>Thanks — we received your pickup request for <strong>${escapeHtml(item)}</strong> in ${escapeHtml(where)}.</p>
<p>No hauler in our network currently covers that ZIP, so nobody will call yet. We’ll keep the request if a matching hauler comes online.</p>
<p><a href="${siteUrl()}">DumpRegistry</a></p>`,
    text: opts.routed
      ? `Hi ${opts.name},\n\nWe sent your ${item} request in ${where} to one hauler covering that ZIP.\n`
      : `Hi ${opts.name},\n\nWe received your ${item} request in ${where}. No hauler covers that ZIP yet.\n`,
  });
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
  let leadId: number | null = null;
  if (db) {
    await ensureMarketplaceSchema(db);
    const inserted = await db`
      INSERT INTO lead_requests (city, state, zip, item_slug, name, email, phone, notes, status)
      VALUES (${city}, ${state}, ${zip}, ${itemSlug}, ${name}, ${email}, ${phone}, ${notes}, 'new')
      RETURNING id
    `;
    leadId = inserted.length ? Number(inserted[0].id) : null;
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

  let routed = false;
  let partnerName: string | null = null;
  if (db && leadId) {
    try {
      const partner = await pickPartnerForZip(db, zip);
      if (partner) {
        await db`
          UPDATE lead_requests
          SET status = 'routed', partner_id = ${partner.id}, routed_at = NOW()
          WHERE id = ${leadId}
        `;
        routed = true;
        partnerName = partner.company;
        const where = `${city}, ${state} ${zip}`;
        const item = itemSlug ?? "pickup";
        await sendEmail({
          to: partner.email,
          subject: `DumpRegistry lead: ${city} ${zip} — ${item}`,
          replyTo: email,
          html: `<p>Hi ${escapeHtml(partner.contact_name ?? partner.company)},</p>
<p>New pickup lead in <strong>${escapeHtml(where)}</strong> (ZIP is in your coverage):</p>
<ul>
<li>Item: ${escapeHtml(item)}</li>
<li>Name: ${escapeHtml(name)}</li>
<li>Email: ${escapeHtml(email)}</li>
<li>Phone: ${escapeHtml(phone)}</li>
<li>Notes: ${escapeHtml(notes ?? "—")}</li>
</ul>
<p>Reply to the customer directly to quote. This used 1 prepaid credit (${partner.lead_credits} left).</p>`,
          text: `New lead in ${where} for ${item}.\n${name} / ${email} / ${phone}\n${notes ?? ""}\n`,
        });
        await maybePauseIfEmpty(db, partner);
      } else {
        await db`UPDATE lead_requests SET status = 'unmatched' WHERE id = ${leadId}`;
      }
    } catch (err) {
      console.error("[leads] route failed", err);
    }
  }

  await notifyResident({ name, email, city, state, zip, itemSlug, routed });

  const ops = opsInbox();
  if (ops) {
    const where = `${city}, ${state} ${zip}`;
    await sendEmail({
      to: ops,
      subject: routed ? `[Lead routed] ${city} ${zip}` : `[Lead unmatched] ${city} ${zip}`,
      replyTo: email,
      html: `<p>${routed ? `Routed to ${escapeHtml(partnerName ?? "partner")}` : "No covering hauler"}</p>
<ul>
<li>Where: ${escapeHtml(where)}</li>
<li>Item: ${escapeHtml(itemSlug ?? "pickup")}</li>
<li>Name: ${escapeHtml(name)}</li>
<li>Email: ${escapeHtml(email)}</li>
<li>Phone: ${escapeHtml(phone)}</li>
<li>Notes: ${escapeHtml(notes ?? "—")}</li>
</ul>`,
    });
  }

  return NextResponse.json({ ok: true, storage: db ? "neon" : "file", routed });
}
