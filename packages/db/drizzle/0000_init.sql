CREATE TABLE IF NOT EXISTS "items" (
  "id" serial PRIMARY KEY NOT NULL,
  "slug" varchar(120) NOT NULL UNIQUE,
  "name" varchar(160) NOT NULL,
  "category" varchar(80) NOT NULL,
  "hazard_default" varchar(40) NOT NULL,
  "badge_default" varchar(40) NOT NULL,
  "fee_band_default" varchar(80) NOT NULL,
  "curbside_default" boolean DEFAULT false NOT NULL,
  "facility_type_default" varchar(120) NOT NULL,
  "summary_default" text NOT NULL
);

CREATE TABLE IF NOT EXISTS "geo_places" (
  "id" serial PRIMARY KEY NOT NULL,
  "zip" varchar(10),
  "city" varchar(120) NOT NULL,
  "city_slug" varchar(140) NOT NULL,
  "state" varchar(2) NOT NULL,
  "state_slug" varchar(40) NOT NULL,
  "lat" double precision,
  "lng" double precision,
  "population" integer DEFAULT 0
);

CREATE TABLE IF NOT EXISTS "rules" (
  "id" serial PRIMARY KEY NOT NULL,
  "item_slug" varchar(120) NOT NULL,
  "state" varchar(2) NOT NULL,
  "city_slug" varchar(140),
  "zip" varchar(10),
  "is_curbside_allowed" boolean,
  "nearest_facility_type" varchar(120),
  "common_disposal_fee" varchar(80),
  "badge" varchar(40),
  "hazard_rating" varchar(40),
  "answer" text,
  "steps_json" text,
  "faqs_json" text,
  "source_url" text NOT NULL,
  "source_name" varchar(200) NOT NULL,
  "last_verified_at" timestamp with time zone NOT NULL,
  "reviewed_by" varchar(120),
  "needs_review" boolean DEFAULT false NOT NULL
);

CREATE TABLE IF NOT EXISTS "facilities" (
  "id" serial PRIMARY KEY NOT NULL,
  "name" varchar(200) NOT NULL,
  "facility_type" varchar(120) NOT NULL,
  "city_slug" varchar(140) NOT NULL,
  "state" varchar(2) NOT NULL,
  "zip" varchar(10),
  "address" text,
  "lat" double precision,
  "lng" double precision,
  "source_url" text
);

CREATE TABLE IF NOT EXISTS "disposal_pages" (
  "id" serial PRIMARY KEY NOT NULL,
  "state_slug" varchar(40) NOT NULL,
  "city_slug" varchar(140) NOT NULL,
  "zip" varchar(10),
  "item_slug" varchar(120) NOT NULL,
  "city" varchar(120) NOT NULL,
  "state" varchar(2) NOT NULL,
  "item_name" varchar(160) NOT NULL,
  "category" varchar(80) NOT NULL,
  "is_curbside_allowed" boolean NOT NULL,
  "nearest_facility_type" varchar(120) NOT NULL,
  "common_disposal_fee" varchar(80) NOT NULL,
  "badge" varchar(40) NOT NULL,
  "hazard_rating" varchar(40) NOT NULL,
  "answer" text NOT NULL,
  "steps_json" text NOT NULL,
  "faqs_json" text NOT NULL,
  "rule_source_level" varchar(20) NOT NULL,
  "source_url" text,
  "source_name" varchar(200),
  "last_verified_at" timestamp with time zone,
  "lat" double precision,
  "lng" double precision,
  "indexable" boolean DEFAULT false NOT NULL,
  "needs_review" boolean DEFAULT false NOT NULL,
  "updated_at" timestamp with time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS "user_submissions" (
  "id" serial PRIMARY KEY NOT NULL,
  "state_slug" varchar(40) NOT NULL,
  "city_slug" varchar(140) NOT NULL,
  "item_slug" varchar(120),
  "message" text NOT NULL,
  "source_url" text,
  "email" varchar(200),
  "status" varchar(40) DEFAULT 'pending' NOT NULL,
  "created_at" timestamp with time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS "lead_requests" (
  "id" serial PRIMARY KEY NOT NULL,
  "city" varchar(120) NOT NULL,
  "state" varchar(2) NOT NULL,
  "item_slug" varchar(120),
  "name" varchar(160) NOT NULL,
  "email" varchar(200) NOT NULL,
  "phone" varchar(40),
  "notes" text,
  "status" varchar(40) DEFAULT 'new' NOT NULL,
  "created_at" timestamp with time zone DEFAULT now()
);

CREATE INDEX IF NOT EXISTS "geo_state_city_idx" ON "geo_places" ("state_slug","city_slug");
CREATE INDEX IF NOT EXISTS "geo_zip_idx" ON "geo_places" ("zip");
CREATE INDEX IF NOT EXISTS "rules_lookup_idx" ON "rules" ("state","city_slug","item_slug");
CREATE UNIQUE INDEX IF NOT EXISTS "disposal_page_unique" ON "disposal_pages" ("state_slug","city_slug","item_slug","zip");
CREATE INDEX IF NOT EXISTS "disposal_indexable_idx" ON "disposal_pages" ("indexable");
