/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  eslint: {
    ignoreDuringBuilds: false,
  },
  typescript: {
    // Enable TypeScript error checking for production builds
    ignoreBuildErrors: false,
  },
  images: {
    unoptimized: true,
  },
  experimental: {
    // Enable server components
    serverComponentsExternalPackages: ['@prisma/client']
  },
  // Increase server request size limit
  serverRuntimeConfig: {
    // Will only be available on the server side
    maxRequestSize: '200mb'
  }
}

export default nextConfig
