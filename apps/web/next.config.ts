import type { NextConfig } from "next";
import path from "node:path";

const nextConfig: NextConfig = {
  outputFileTracingRoot: path.join(__dirname, "../.."),
  experimental: {
    externalDir: true,
  },
  outputFileTracingIncludes: {
    "/api/partners/**": ["../../data/geo/zip_index.json"],
  },
};

export default nextConfig;
