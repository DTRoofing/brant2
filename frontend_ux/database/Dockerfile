FROM postgres:15-alpine

# Set environment variables
ENV POSTGRES_DB=brant_roofing
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

# Copy initialization scripts
COPY ./init-scripts/ /docker-entrypoint-initdb.d/

# Create data directory
RUN mkdir -p /var/lib/postgresql/data

# Expose PostgreSQL port
EXPOSE 5432
