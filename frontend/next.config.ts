import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  output: 'export', // <- this replaces `next export`
  trailingSlash: true, // optional: helps with static file serving
};

export default nextConfig;
