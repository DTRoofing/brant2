#!/bin/bash
# Test Cloud SQL Proxy connection

echo "🔍 Testing Cloud SQL Proxy Connection"
echo "===================================="

# Check if proxy is running
if ! nc -z localhost 5433 2>/dev/null; then
    echo "❌ Cloud SQL Proxy is not running on localhost:5433"
    echo "   Please run: ./start-cloud-sql-proxy.sh"
    exit 1
fi

echo "✅ Cloud SQL Proxy is running on localhost:5433"

# Test connection
echo ""
echo "🔄 Testing database connection through proxy..."

# Using Docker to test with psql
docker run --rm --network host postgres:15-alpine psql \
    "postgresql://ADMIN:Brant01!@localhost:5433/postgres" \
    -c "SELECT version();" \
    -c "SELECT current_database(), current_user;" \
    -c "SELECT 'Connection successful!' as status;"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully connected to Cloud SQL through proxy!"
    echo ""
    echo "📝 You can now use this connection string in your application:"
    echo "   DATABASE_URL=\"postgresql://ADMIN:Brant01!@localhost:5433/postgres?schema=public\""
else
    echo ""
    echo "❌ Connection failed. Please check:"
    echo "   1. Cloud SQL Proxy is running"
    echo "   2. Credentials are correct"
    echo "   3. Service account has proper permissions"
fi