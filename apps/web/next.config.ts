import type { NextConfig } from "next";
import path from "node:path";

const nextConfig: NextConfig = {
  outputFileTracingRoot: path.join(__dirname, "../.."),
  // Cloudflare / static-export friendly when using OpenNext later
  experimental: {
    externalDir: true,
  },
};

export default nextConfig;
