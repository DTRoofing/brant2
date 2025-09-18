# ---- Base Stage ----
# This stage installs all dependencies using npm.
# It's used as a foundation for other stages to leverage Docker's build cache.
FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm install


# ---- Development Stage ----
# This stage is for local development. It runs the Next.js dev server,
# which supports hot-reloading. The source code is mounted as a volume
# in docker-compose, so changes are reflected instantly.
FROM base AS development
WORKDIR /app
# Copy the rest of the app. This will be overwritten by the volume mount,
# but it's good practice to have it here for standalone builds.
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]


# ---- Builder Stage ----
# This stage builds the application for production. It creates an optimized
# build, including the standalone server output if configured.
FROM base AS builder
WORKDIR /app
COPY . .
# The NEXT_PUBLIC_API_URL is a build-time argument that gets baked into the static assets.
# It should be passed from docker-compose for the production build.
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
RUN npm run build


# ---- Production Stage ----
# This is the final, minimal image for production. It uses the standalone
# output from the builder stage for a small footprint and better security.
#
# IMPORTANT: To use this stage, you must enable the standalone output in your next.config.mjs:
# /** @type {import('next').NextConfig} */
# const nextConfig = {
#   output: 'standalone',
# };
# module.exports = nextConfig;
#
FROM node:20-alpine AS production
WORKDIR /app

ENV NODE_ENV=production

# Create a non-root user for security.
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Copy the standalone server output from the builder stage.
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
# Copy the public assets.
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
# Copy the static assets from the build.
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

# Cloud Run provides the PORT environment variable, which Next.js's standalone server
# automatically uses. The default is 3000 if PORT is not set.
EXPOSE 3000

# The standalone server is started.
CMD ["node", "server.js"]