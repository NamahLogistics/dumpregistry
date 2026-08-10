import postgres from "postgres";

let sql: ReturnType<typeof postgres> | null = null;

export function getSql() {
  const url = process.env.DATABASE_URL;
  if (!url) return null;
  if (!sql) {
    sql = postgres(url, { max: 3, ssl: "require", prepare: false });
  }
  return sql;
}
