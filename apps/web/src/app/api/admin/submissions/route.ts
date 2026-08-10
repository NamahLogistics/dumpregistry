import { NextResponse } from "next/server";
import { getSql } from "@/lib/db";

function authorized(req: Request) {
  const token = process.env.ADMIN_TOKEN;
  if (!token) return false;
  const header = req.headers.get("authorization") ?? "";
  return header === `Bearer ${token}`;
}

export async function GET(req: Request) {
  if (!authorized(req)) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }
  const db = getSql();
  if (!db) {
    return NextResponse.json({ error: "DATABASE_URL required for review queue" }, { status: 503 });
  }
  const rows = await db`
    SELECT id, state_slug, city_slug, item_slug, message, source_url, email, status, created_at
    FROM user_submissions
    WHERE status = 'pending'
    ORDER BY created_at DESC
    LIMIT 200
  `;
  return NextResponse.json({ submissions: rows });
}

type PatchBody = {
  id?: number;
  status?: "approved" | "rejected" | "needs_more_info";
};

/**
 * Review-only: never auto-publishes disposal answers.
 * Approvals require a source_url so editors can manually verify before writing rules.
 */
export async function PATCH(req: Request) {
  if (!authorized(req)) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }
  const body = (await req.json()) as PatchBody;
  const id = Number(body.id);
  const status = body.status;
  if (!id || !status || !["approved", "rejected", "needs_more_info"].includes(status)) {
    return NextResponse.json({ error: "Invalid payload" }, { status: 400 });
  }

  const db = getSql();
  if (!db) {
    return NextResponse.json({ error: "DATABASE_URL required for review queue" }, { status: 503 });
  }

  const existing = await db`
    SELECT id, source_url, status FROM user_submissions WHERE id = ${id} LIMIT 1
  `;
  if (!existing.length) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }
  const row = existing[0];
  if (status === "approved" && !row.source_url) {
    return NextResponse.json(
      { error: "Cannot approve without source_url — never auto-publish unsourced claims" },
      { status: 400 },
    );
  }

  await db`
    UPDATE user_submissions SET status = ${status} WHERE id = ${id}
  `;
  return NextResponse.json({
    ok: true,
    id,
    status,
    published: false,
    note: "Review status saved only. Editors must manually verify and update rule JSON — no auto-publish.",
  });
}
