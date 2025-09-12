-- Database initialization script for Docker container
-- Create the main database if it doesn't exist
SELECT 'CREATE DATABASE brant_roofing'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'brant_roofing')\gexec

-- Connect to the database
\c brant_roofing;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set timezone
SET timezone = 'UTC';
