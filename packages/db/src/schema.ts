import {
  boolean,
  doublePrecision,
  index,
  integer,
  pgTable,
  serial,
  text,
  timestamp,
  uniqueIndex,
  varchar,
} from "drizzle-orm/pg-core";

export const items = pgTable("items", {
  id: serial("id").primaryKey(),
  slug: varchar("slug", { length: 120 }).notNull().unique(),
  name: varchar("name", { length: 160 }).notNull(),
  category: varchar("category", { length: 80 }).notNull(),
  hazardDefault: varchar("hazard_default", { length: 40 }).notNull(),
  badgeDefault: varchar("badge_default", { length: 40 }).notNull(),
  feeBandDefault: varchar("fee_band_default", { length: 80 }).notNull(),
  curbsideDefault: boolean("curbside_default").notNull().default(false),
  facilityTypeDefault: varchar("facility_type_default", { length: 120 }).notNull(),
  summaryDefault: text("summary_default").notNull(),
});

export const geoPlaces = pgTable(
  "geo_places",
  {
    id: serial("id").primaryKey(),
    zip: varchar("zip", { length: 10 }),
    city: varchar("city", { length: 120 }).notNull(),
    citySlug: varchar("city_slug", { length: 140 }).notNull(),
    state: varchar("state", { length: 2 }).notNull(),
    stateSlug: varchar("state_slug", { length: 40 }).notNull(),
    lat: doublePrecision("lat"),
    lng: doublePrecision("lng"),
    population: integer("population").default(0),
  },
  (t) => [
    index("geo_state_city_idx").on(t.stateSlug, t.citySlug),
    index("geo_zip_idx").on(t.zip),
  ],
);

export const rules = pgTable(
  "rules",
  {
    id: serial("id").primaryKey(),
    itemSlug: varchar("item_slug", { length: 120 }).notNull(),
    state: varchar("state", { length: 2 }).notNull(),
    citySlug: varchar("city_slug", { length: 140 }),
    zip: varchar("zip", { length: 10 }),
    isCurbsideAllowed: boolean("is_curbside_allowed"),
    nearestFacilityType: varchar("nearest_facility_type", { length: 120 }),
    commonDisposalFee: varchar("common_disposal_fee", { length: 80 }),
    badge: varchar("badge", { length: 40 }),
    hazardRating: varchar("hazard_rating", { length: 40 }),
    answer: text("answer"),
    stepsJson: text("steps_json"),
    faqsJson: text("faqs_json"),
    sourceUrl: text("source_url").notNull(),
    sourceName: varchar("source_name", { length: 200 }).notNull(),
    lastVerifiedAt: timestamp("last_verified_at", { withTimezone: true }).notNull(),
    reviewedBy: varchar("reviewed_by", { length: 120 }),
    needsReview: boolean("needs_review").notNull().default(false),
  },
  (t) => [
    index("rules_lookup_idx").on(t.state, t.citySlug, t.itemSlug),
  ],
);

export const facilities = pgTable("facilities", {
  id: serial("id").primaryKey(),
  name: varchar("name", { length: 200 }).notNull(),
  facilityType: varchar("facility_type", { length: 120 }).notNull(),
  citySlug: varchar("city_slug", { length: 140 }).notNull(),
  state: varchar("state", { length: 2 }).notNull(),
  zip: varchar("zip", { length: 10 }),
  address: text("address"),
  lat: doublePrecision("lat"),
  lng: doublePrecision("lng"),
  sourceUrl: text("source_url"),
});

export const disposalPages = pgTable(
  "disposal_pages",
  {
    id: serial("id").primaryKey(),
    stateSlug: varchar("state_slug", { length: 40 }).notNull(),
    citySlug: varchar("city_slug", { length: 140 }).notNull(),
    zip: varchar("zip", { length: 10 }),
    itemSlug: varchar("item_slug", { length: 120 }).notNull(),
    city: varchar("city", { length: 120 }).notNull(),
    state: varchar("state", { length: 2 }).notNull(),
    itemName: varchar("item_name", { length: 160 }).notNull(),
    category: varchar("category", { length: 80 }).notNull(),
    isCurbsideAllowed: boolean("is_curbside_allowed").notNull(),
    nearestFacilityType: varchar("nearest_facility_type", { length: 120 }).notNull(),
    commonDisposalFee: varchar("common_disposal_fee", { length: 80 }).notNull(),
    badge: varchar("badge", { length: 40 }).notNull(),
    hazardRating: varchar("hazard_rating", { length: 40 }).notNull(),
    answer: text("answer").notNull(),
    stepsJson: text("steps_json").notNull(),
    faqsJson: text("faqs_json").notNull(),
    ruleSourceLevel: varchar("rule_source_level", { length: 20 }).notNull(),
    sourceUrl: text("source_url"),
    sourceName: varchar("source_name", { length: 200 }),
    lastVerifiedAt: timestamp("last_verified_at", { withTimezone: true }),
    lat: doublePrecision("lat"),
    lng: doublePrecision("lng"),
    indexable: boolean("indexable").notNull().default(false),
    needsReview: boolean("needs_review").notNull().default(false),
    updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow(),
  },
  (t) => [
    uniqueIndex("disposal_page_unique").on(t.stateSlug, t.citySlug, t.itemSlug, t.zip),
    index("disposal_indexable_idx").on(t.indexable),
  ],
);

export const userSubmissions = pgTable("user_submissions", {
  id: serial("id").primaryKey(),
  stateSlug: varchar("state_slug", { length: 40 }).notNull(),
  citySlug: varchar("city_slug", { length: 140 }).notNull(),
  itemSlug: varchar("item_slug", { length: 120 }),
  message: text("message").notNull(),
  sourceUrl: text("source_url"),
  email: varchar("email", { length: 200 }),
  status: varchar("status", { length: 40 }).notNull().default("pending"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
});

export const leadRequests = pgTable("lead_requests", {
  id: serial("id").primaryKey(),
  city: varchar("city", { length: 120 }).notNull(),
  state: varchar("state", { length: 2 }).notNull(),
  zip: varchar("zip", { length: 16 }),
  itemSlug: varchar("item_slug", { length: 120 }),
  name: varchar("name", { length: 160 }).notNull(),
  email: varchar("email", { length: 200 }).notNull(),
  phone: varchar("phone", { length: 40 }),
  notes: text("notes"),
  status: varchar("status", { length: 40 }).notNull().default("new"),
  partnerId: integer("partner_id"),
  routedAt: timestamp("routed_at", { withTimezone: true }),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
});

export const partnerApplications = pgTable("partner_applications", {
  id: serial("id").primaryKey(),
  company: varchar("company", { length: 160 }).notNull(),
  contactName: varchar("contact_name", { length: 120 }).notNull(),
  email: varchar("email", { length: 200 }).notNull(),
  phone: varchar("phone", { length: 40 }),
  cities: text("cities").notNull(),
  services: text("services").notNull(),
  notes: text("notes"),
  plan: varchar("plan", { length: 40 }).default("trial"),
  status: varchar("status", { length: 40 }).notNull().default("pending"),
  shopZip: varchar("shop_zip", { length: 16 }),
  coverageZips: text("coverage_zips"),
  radiusMiles: integer("radius_miles"),
  attestAt: timestamp("attest_at", { withTimezone: true }),
  dodoCustomerId: varchar("dodo_customer_id", { length: 80 }),
  leadCredits: integer("lead_credits").notNull().default(0),
  leadsRoutedCount: integer("leads_routed_count").notNull().default(0),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
});

export const dodoPayments = pgTable("dodo_payments", {
  id: serial("id").primaryKey(),
  paymentId: varchar("payment_id", { length: 80 }).notNull().unique(),
  partnerId: integer("partner_id").notNull(),
  creditsGranted: integer("credits_granted").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
});
