import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "./schema";

export function createDb(connectionString = process.env.DATABASE_URL) {
  if (!connectionString) {
    throw new Error("DATABASE_URL is required for Postgres access");
  }
  const client = postgres(connectionString, {
    max: 5,
    ssl: "require",
    prepare: false,
    connect_timeout: 30,
  });
  return drizzle(client, { schema });
}

export type Db = ReturnType<typeof createDb>;
