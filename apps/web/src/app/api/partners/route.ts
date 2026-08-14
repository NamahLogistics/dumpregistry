import { NextResponse } from "next/server";
import { expandCoverage, parseZipList } from "@/lib/coverage";
import { dodoConfigured, TRIAL_CREDITS } from "@/lib/dodo";
import { getSql } from "@/lib/db";
import { escapeHtml, opsInbox, sendEmail } from "@/lib/email";
import { ensureMarketplaceSchema } from "@/lib/marketplace-schema";
import { checkoutOrError } from "@/lib/partner-billing";

export async function POST(req: Request) {
  const body = await req.json();
  const company = String(body.company ?? "").trim();
  const contactName = String(body.contactName ?? "").trim();
  const email = String(body.email ?? "").trim();
  const phone = body.phone ? String(body.phone).trim() : null;
  const services = String(body.services ?? "").trim();
  const notes = body.notes ? String(body.notes).trim() : null;
  const plan = String(body.plan ?? "trial").trim() === "pack" ? "pack" : "trial";
  const attested = body.attest === true || body.attest === "true" || body.attest === "on";
  const shopZip = String(body.shopZip ?? "").trim();
  const extraZips = parseZipList(body.coverageZips);
  const radiusRaw = body.radiusMiles === "" || body.radiusMiles == null ? null : Number(body.radiusMiles);
  const radiusMiles = radiusRaw == null || Number.isNaN(radiusRaw) ? null : radiusRaw;

  if (!company || !contactName || !email.includes("@") || services.length < 3 || !attested) {
    return NextResponse.json({ error: "Invalid partner application" }, { status: 400 });
  }

  let coverage: ReturnType<typeof expandCoverage>;
  try {
    coverage = expandCoverage({ shopZip, extraZips, radiusMiles });
  } catch (err) {
    return NextResponse.json({ error: err instanceof Error ? err.message : "Invalid coverage" }, { status: 400 });
  }

  const db = getSql();
  if (!db) {
    return NextResponse.json({ error: "Database required for partner onboarding" }, { status: 503 });
  }

  await ensureMarketplaceSchema(db);

  const status = plan === "trial" ? "active" : "pending_payment";
  const credits = plan === "trial" ? TRIAL_CREDITS : 0;

  const inserted = await db`
    INSERT INTO partner_applications (
      company, contact_name, email, phone, cities, services, notes, plan, status,
      shop_zip, coverage_zips, radius_miles, attest_at, lead_credits
    )
    VALUES (
      ${company}, ${contactName}, ${email}, ${phone}, ${coverage.summary}, ${services}, ${notes},
      ${plan}, ${status}, ${shopZip.replace(/\D/g, "").slice(0, 5)}, ${db.json(coverage.zips)},
      ${radiusMiles}, NOW(), ${credits}
    )
    RETURNING id, email, contact_name, company
  `;
  const partner = inserted[0];
  if (!partner) {
    return NextResponse.json({ error: "Could not save application" }, { status: 500 });
  }

  const site = process.env.NEXT_PUBLIC_SITE_URL ?? "https://www.dumpregistry.org";
  await sendEmail({
    to: email,
    subject:
      plan === "trial"
        ? "You’re live on DumpRegistry — 10 trial leads"
        : "DumpRegistry partner application — complete payment",
    html:
      plan === "trial"
        ? `<p>Hi ${escapeHtml(contactName)},</p>
<p><strong>${escapeHtml(company)}</strong> is active for jobs in ${escapeHtml(coverage.summary)}.</p>
<p>You have ${TRIAL_CREDITS} trial leads. After that we email a Dodo checkout for a 10-lead pack ($250). We only send a job whose ZIP is in your coverage.</p>
<p><a href="${site}/partners">Partners</a></p>`
        : `<p>Hi ${escapeHtml(contactName)},</p>
<p>We saved coverage for <strong>${escapeHtml(company)}</strong> (${escapeHtml(coverage.summary)}). Complete the 10-lead pack to go live — Dodo will confirm payment automatically.</p>`,
  });

  const ops = opsInbox();
  if (ops) {
    await sendEmail({
      to: ops,
      subject: `[Partner] ${company} — ${coverage.summary}`,
      replyTo: email,
      html: `<p>New partner ${escapeHtml(plan)} — no admin activate needed.</p>
<ul>
<li>Company: ${escapeHtml(company)}</li>
<li>Email: ${escapeHtml(email)}</li>
<li>Coverage: ${escapeHtml(coverage.summary)}</li>
<li>ZIPs: ${coverage.zips.length}</li>
<li>Status: ${escapeHtml(status)}</li>
</ul>`,
    });
  }

  if (plan === "trial") {
    return NextResponse.json({
      ok: true,
      status: "active",
      credits: TRIAL_CREDITS,
      zipCount: coverage.zips.length,
    });
  }

  if (!dodoConfigured()) {
    return NextResponse.json(
      {
        ok: true,
        status: "pending_payment",
        error: "Saved coverage, but Dodo checkout is not configured yet. We will email a pay link when it is.",
        zipCount: coverage.zips.length,
      },
      { status: 200 },
    );
  }

  const checkout = await checkoutOrError({
    id: Number(partner.id),
    email: String(partner.email),
    contact_name: String(partner.contact_name),
    company: String(partner.company),
  });
  if (!checkout.ok) {
    return NextResponse.json(
      { ok: true, status: "pending_payment", error: checkout.error, zipCount: coverage.zips.length },
      { status: 200 },
    );
  }
  return NextResponse.json({
    ok: true,
    status: "pending_payment",
    checkoutUrl: checkout.checkoutUrl,
    zipCount: coverage.zips.length,
  });
}
