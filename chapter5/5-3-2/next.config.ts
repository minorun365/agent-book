import type {NextConfig} from "next";

const nextConfig: NextConfig = {
  // Mastraを外部パッケージとして設定
  serverExternalPackages: ["@mastra/*"],
}

export default nextConfig;
