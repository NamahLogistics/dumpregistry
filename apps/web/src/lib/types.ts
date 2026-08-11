export type Item = {
  slug: string;
  name: string;
  category: string;
  hazard_default: string;
  badge_default: string;
  fee_band_default: string;
  curbside_default: boolean;
  facility_type_default: string;
  summary_default: string;
};

export type City = {
  city: string;
  city_slug: string;
  state: string;
  state_slug: string;
  lat: number;
  lng: number;
  population: number;
};

export type Faq = { q: string; a: string };

export type Facility = {
  name: string;
  facility_type: string;
  city_slug: string;
  state: string;
  zip?: string | null;
  address?: string | null;
  lat?: number | null;
  lng?: number | null;
  source_url?: string | null;
  hours?: string | null;
  phone?: string | null;
  /** Item slugs this site typically accepts — used by /centers finder. */
  accepted_materials?: string[];
};

export type DisposalPage = {
  state_slug: string;
  city_slug: string;
  zip: string | null;
  item_slug: string;
  city: string;
  state: string;
  item_name: string;
  category: string;
  is_curbside_allowed: boolean;
  nearest_facility_type: string;
  common_disposal_fee: string;
  badge: string;
  hazard_rating: string;
  answer: string;
  steps: string[];
  faqs: Faq[];
  rule_source_level: "city" | "state" | "default" | string;
  source_url: string | null;
  source_name: string | null;
  last_verified_at: string | null;
  lat: number | null;
  lng: number | null;
  indexable: boolean;
  needs_review: boolean;
  facilities?: Facility[];
  nearby_zips?: string[];
};

export type ZipHub = {
  state_slug: string;
  city_slug: string;
  zip: string;
  city: string;
  state: string;
  lat: number | null;
  lng: number | null;
  population: number;
  indexable: boolean;
  facilities?: Facility[];
};
