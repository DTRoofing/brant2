# ---- Base Stage ----
# Use a specific Node.js version for reproducibility.
FROM node:18-alpine AS base

# Set the working directory in the container.
WORKDIR /app

# Copy package.json and package-lock.json to leverage Docker cache.
COPY package.json ./
COPY package-lock.json ./


# ---- Dependencies Stage ----
# This stage only installs dependencies. It's a separate stage to improve caching.
FROM base AS deps

# Install dependencies.
RUN npm install


# ---- Development Stage ----
# This stage is used for local development. It runs the Next.js dev server.
# It relies on volume mounts from docker-compose.yml for hot-reloading.
FROM base AS development

# Copy dependencies from the 'deps' stage.
COPY --from=deps /app/node_modules ./node_modules

# Copy the rest of the application code.
COPY . .

# Expose the port Next.js runs on.
# Uses PORT environment variable (Cloud Run sets this to 8080) or defaults to 3000 for local dev
EXPOSE ${PORT:-3000}

# Command to start the development server.
CMD ["npm", "run", "dev"]


# ---- Production Stage ----
# This stage builds the application for production.
FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# ---- Release Stage ----
# This is the final, minimal image for production.
FROM base AS release

# Create nextjs user for security
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to nextjs user
USER nextjs

# The Next.js standalone output uses PORT environment variable (Cloud Run sets this to 8080) or defaults to 3000
EXPOSE ${PORT:-3000}

# Command to start the production server.
CMD ["node", "server.js"]