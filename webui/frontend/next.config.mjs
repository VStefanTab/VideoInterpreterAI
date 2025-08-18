/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Allow cross-origin requests from the stream server
  allowedDevOrigins: ['http://localhost:2000']
};

export default nextConfig;
