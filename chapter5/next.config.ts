import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  serverExternalPackages: ["@mastra/*"],
  // env: {
  //   AWS_REGION: process.env.AWS_REGION || "us-east-1",
  //   GITHUB_TOKEN: process.env.GITHUB_TOKEN || "",
  //   CONFLUENCE_BASE_URL: process.env.CONFLUENCE_BASE_URL || "",
  //   CONFLUENCE_API_TOKEN: process.env.CONFLUENCE_API_TOKEN || "",
  //   CONFLUENCE_USER_EMAIL: process.env.CONFLUENCE_USER_EMAIL || "",
  // },
};

export default nextConfig;
