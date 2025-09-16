/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: false,  // Enable TypeScript checking for production safety
  },
  images: {
    unoptimized: true,
  },
  experimental: {
    // Enable server components
    serverComponentsExternalPackages: ['@prisma/client', '@google-cloud/documentai', '@google-cloud/vision', '@google-cloud/storage']
  },
  // Increase server request size limit
  serverRuntimeConfig: {
    // Will only be available on the server side
    maxRequestSize: '200mb'
  }
}

export default nextConfig
