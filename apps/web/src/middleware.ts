import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/** AdSense crawls the apex host and does not treat a www 308 as ads.txt found. */
const APEX = "dumpregistry.org";
const WWW = "www.dumpregistry.org";
const SKIP = new Set(["/ads.txt", "/robots.txt"]);

export function middleware(req: NextRequest) {
  const host = (req.headers.get("host") ?? "").split(":")[0].toLowerCase();
  if (host !== APEX) return NextResponse.next();
  if (SKIP.has(req.nextUrl.pathname)) return NextResponse.next();

  const url = req.nextUrl.clone();
  url.protocol = "https:";
  url.hostname = WWW;
  url.port = "";
  return NextResponse.redirect(url, 301);
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
