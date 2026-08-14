import type { getSql } from "./db";

type Db = NonNullable<ReturnType<typeof getSql>>;

/** Idempotent Neon columns for the automated hauler desk. */
export async function ensureMarketplaceSchema(db: Db) {
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
      plan VARCHAR(40) DEFAULT 'trial',
      status VARCHAR(40) NOT NULL DEFAULT 'pending',
      created_at TIMESTAMPTZ DEFAULT NOW()
    )
  `;
  await db`
    CREATE TABLE IF NOT EXISTS lead_requests (
      id SERIAL PRIMARY KEY,
      city VARCHAR(120) NOT NULL,
      state VARCHAR(8) NOT NULL,
      item_slug VARCHAR(120),
      name VARCHAR(160) NOT NULL,
      email VARCHAR(200) NOT NULL,
      phone VARCHAR(40),
      notes TEXT,
      status VARCHAR(40) NOT NULL DEFAULT 'new',
      created_at TIMESTAMPTZ DEFAULT NOW()
    )
  `;
  await db`ALTER TABLE partner_applications ADD COLUMN IF NOT EXISTS plan VARCHAR(40) DEFAULT 'trial'`;
  await db`ALTER TABLE partner_applications ADD COLUMN IF NOT EXISTS shop_zip VARCHAR(16)`;
  await db`ALTER TABLE partner_applications ADD COLUMN IF NOT EXISTS coverage_zips JSONB`;
  await db`ALTER TABLE partner_applications ADD COLUMN IF NOT EXISTS radius_miles INTEGER`;
  await db`ALTER TABLE partner_applications ADD COLUMN IF NOT EXISTS attest_at TIMESTAMPTZ`;
  await db`ALTER TABLE partner_applications ADD COLUMN IF NOT EXISTS dodo_customer_id VARCHAR(80)`;
  await db`ALTER TABLE partner_applications ADD COLUMN IF NOT EXISTS lead_credits INTEGER NOT NULL DEFAULT 0`;
  await db`ALTER TABLE partner_applications ADD COLUMN IF NOT EXISTS leads_routed_count INTEGER NOT NULL DEFAULT 0`;

  await db`ALTER TABLE lead_requests ADD COLUMN IF NOT EXISTS zip VARCHAR(16)`;
  await db`ALTER TABLE lead_requests ADD COLUMN IF NOT EXISTS partner_id INTEGER`;
  await db`ALTER TABLE lead_requests ADD COLUMN IF NOT EXISTS routed_at TIMESTAMPTZ`;

  await db`
    CREATE TABLE IF NOT EXISTS dodo_payments (
      id SERIAL PRIMARY KEY,
      payment_id VARCHAR(80) NOT NULL UNIQUE,
      partner_id INTEGER NOT NULL,
      credits_granted INTEGER NOT NULL,
      created_at TIMESTAMPTZ DEFAULT NOW()
    )
  `;
}

export type PartnerRow = {
  id: number;
  company: string;
  contact_name: string;
  email: string;
  phone: string | null;
  cities: string;
  services: string;
  notes: string | null;
  plan: string | null;
  status: string;
  shop_zip: string | null;
  coverage_zips: unknown;
  radius_miles: number | null;
  dodo_customer_id: string | null;
  lead_credits: number;
  leads_routed_count: number;
  created_at: string | Date;
};
