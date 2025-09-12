#!/bin/bash

set -e

# Create application user with proper permissions
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "brant_roofing" <<-EOSQL
    -- Create application user
    CREATE USER app_user WITH PASSWORD 'app_password';
    
    -- Grant necessary permissions
    GRANT CONNECT ON DATABASE brant_roofing TO app_user;
    GRANT USAGE ON SCHEMA public TO app_user;
    GRANT CREATE ON SCHEMA public TO app_user;
    
    -- Grant permissions on all tables (for existing and future tables)
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user;
    
    -- Set default privileges for future objects
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO app_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO app_user;
EOSQL

echo "Database permissions configured successfully"
