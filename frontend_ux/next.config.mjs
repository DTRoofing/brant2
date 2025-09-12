/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  experimental: {
    // Enable server components
    serverComponentsExternalPackages: ['@prisma/client', '@google-cloud/documentai', '@google-cloud/vision', '@google-cloud/storage']
  }
}

export default nextConfig
