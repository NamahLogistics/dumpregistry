import { existsSync } from "node:fs";
import path from "node:path";

/** Resolve data/ whether running from repo root, apps/web, or Vercel. */
export function dataRoot() {
  const candidates = [
    process.env.DATA_DIR,
    path.resolve(process.cwd(), "data"),
    path.resolve(process.cwd(), "../../data"),
    path.resolve(__dirname, "../../../../data"),
  ].filter(Boolean) as string[];

  for (const candidate of candidates) {
    if (existsSync(candidate)) return candidate;
  }
  return path.resolve(process.cwd(), "../../data");
}

export function contentRoot() {
  const candidates = [
    path.resolve(process.cwd(), "content"),
    path.resolve(process.cwd(), "../../content"),
    path.resolve(__dirname, "../../../../content"),
  ];
  for (const candidate of candidates) {
    if (existsSync(candidate)) return candidate;
  }
  return path.resolve(process.cwd(), "../../content");
}
