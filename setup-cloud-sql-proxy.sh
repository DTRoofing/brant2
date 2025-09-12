#!/bin/bash
# Setup script for Google Cloud SQL Proxy

set -e

echo "🔧 Google Cloud SQL Proxy Setup Script"
echo "======================================"

# Configuration
PROJECT_ID="brant-roofing-system-2025"
INSTANCE_CONNECTION_NAME="${PROJECT_ID}:us-central1:brant-db"
PROXY_PORT="5433"  # Local port for proxy (avoid conflict with local PostgreSQL)

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if authenticated
echo "🔍 Checking Google Cloud authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="get(account)" &> /dev/null; then
    echo "📝 Please authenticate with Google Cloud:"
    gcloud auth login
fi

# Set project
echo "📁 Setting project to: ${PROJECT_ID}"
gcloud config set project ${PROJECT_ID}

# Download Cloud SQL Proxy if not exists
PROXY_DIR="./cloud-sql-proxy"
PROXY_BIN="${PROXY_DIR}/cloud-sql-proxy"

if [ ! -f "${PROXY_BIN}" ]; then
    echo "📥 Downloading Cloud SQL Proxy..."
    mkdir -p ${PROXY_DIR}
    
    # Detect OS and architecture
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    
    if [ "$ARCH" = "x86_64" ]; then
        ARCH="amd64"
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
        ARCH="arm64"
    fi
    
    DOWNLOAD_URL="https://dl.google.com/cloudsql/cloud-sql-proxy.${OS}.${ARCH}"
    
    echo "📦 Downloading from: ${DOWNLOAD_URL}"
    curl -o ${PROXY_BIN} ${DOWNLOAD_URL}
    chmod +x ${PROXY_BIN}
    echo "✅ Cloud SQL Proxy downloaded successfully"
else
    echo "✅ Cloud SQL Proxy already exists"
fi

# Create service account if needed
SERVICE_ACCOUNT_NAME="brant-sql-proxy"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="./cloud-sql-proxy-key.json"

if [ ! -f "${KEY_FILE}" ]; then
    echo "🔑 Creating service account for Cloud SQL Proxy..."
    
    # Create service account
    gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
        --display-name="Cloud SQL Proxy Service Account" \
        --project=${PROJECT_ID} 2>/dev/null || echo "Service account might already exist"
    
    # Grant Cloud SQL Client role
    echo "🔐 Granting Cloud SQL Client role..."
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="roles/cloudsql.client" \
        --quiet
    
    # Create and download key
    echo "📥 Downloading service account key..."
    gcloud iam service-accounts keys create ${KEY_FILE} \
        --iam-account=${SERVICE_ACCOUNT_EMAIL} \
        --project=${PROJECT_ID}
    
    echo "✅ Service account configured"
else
    echo "✅ Service account key already exists"
fi

# Create systemd service file (optional)
echo "📝 Creating systemd service file..."
cat > cloud-sql-proxy.service << EOF
[Unit]
Description=Google Cloud SQL Proxy
After=network.target

[Service]
Type=simple
ExecStart=${PWD}/${PROXY_BIN} \\
    --address=0.0.0.0 \\
    --port=${PROXY_PORT} \\
    --credentials-file=${PWD}/${KEY_FILE} \\
    ${INSTANCE_CONNECTION_NAME}
Restart=on-failure
RestartSec=10
StandardOutput=journal
User=$(whoami)
WorkingDirectory=${PWD}

[Install]
WantedBy=multi-user.target
EOF

# Create start script
echo "📝 Creating start script..."
cat > start-cloud-sql-proxy.sh << 'EOF'
#!/bin/bash
# Start Cloud SQL Proxy

PROXY_PORT=5433
INSTANCE_CONNECTION_NAME="brant-roofing-system-2025:us-central1:brant-db"
KEY_FILE="./cloud-sql-proxy-key.json"
PROXY_BIN="./cloud-sql-proxy/cloud-sql-proxy"

if [ ! -f "${PROXY_BIN}" ]; then
    echo "❌ Cloud SQL Proxy not found. Please run setup-cloud-sql-proxy.sh first"
    exit 1
fi

if [ ! -f "${KEY_FILE}" ]; then
    echo "❌ Service account key not found. Please run setup-cloud-sql-proxy.sh first"
    exit 1
fi

echo "🚀 Starting Cloud SQL Proxy..."
echo "📍 Proxy will listen on localhost:${PROXY_PORT}"
echo "🔗 Connecting to: ${INSTANCE_CONNECTION_NAME}"
echo ""
echo "📝 Use this connection string in your application:"
echo "   postgresql://Admin:Brant01!@localhost:${PROXY_PORT}/postgres?schema=public"
echo ""
echo "Press Ctrl+C to stop the proxy"
echo ""

${PROXY_BIN} \
    --address=127.0.0.1 \
    --port=${PROXY_PORT} \
    --credentials-file=${KEY_FILE} \
    ${INSTANCE_CONNECTION_NAME}
EOF

chmod +x start-cloud-sql-proxy.sh

# Create Docker Compose override for Cloud SQL Proxy
echo "📝 Creating Docker Compose configuration..."
cat > docker-compose.cloud-sql.yml << 'EOF'
version: '3.8'

services:
  # Cloud SQL Proxy service
  cloud-sql-proxy:
    image: gcr.io/cloud-sql-connectors/cloud-sql-proxy:latest
    container_name: cloud-sql-proxy
    command:
      - "--address=0.0.0.0"
      - "--port=5432"
      - "--credentials-file=/config/cloud-sql-proxy-key.json"
      - "brant-roofing-system-2025:us-central1:brant-db"
    volumes:
      - ./cloud-sql-proxy-key.json:/config/cloud-sql-proxy-key.json:ro
    ports:
      - "5433:5432"
    networks:
      - brant-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "nc", "-z", "localhost", "5432"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Override API service to use Cloud SQL
  api:
    environment:
      - DATABASE_URL=postgresql://Admin:Brant01!@cloud-sql-proxy:5432/postgres?schema=public
    depends_on:
      cloud-sql-proxy:
        condition: service_healthy
    networks:
      - brant-network

  # Override worker service to use Cloud SQL
  worker:
    environment:
      - DATABASE_URL=postgresql://Admin:Brant01!@cloud-sql-proxy:5432/postgres?schema=public
    depends_on:
      cloud-sql-proxy:
        condition: service_healthy
    networks:
      - brant-network

networks:
  brant-network:
    driver: bridge
EOF

# Update .env.cloud-sql file
echo "📝 Creating .env.cloud-sql file..."
cat > .env.cloud-sql << 'EOF'
# Cloud SQL Proxy Connection
# When using Cloud SQL Proxy locally
DATABASE_URL_LOCAL="postgresql://Admin:Brant01!@localhost:5433/postgres?schema=public"

# When using Cloud SQL Proxy in Docker
DATABASE_URL="postgresql://Admin:Brant01!@cloud-sql-proxy:5432/postgres?schema=public"

# Direct connection (requires IP whitelist)
DATABASE_URL_DIRECT="postgresql://Admin:Brant01!@34.63.109.196:5432/postgres?sslmode=require&schema=public"
EOF

echo ""
echo "✅ Cloud SQL Proxy setup complete!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. To start Cloud SQL Proxy locally:"
echo "   ./start-cloud-sql-proxy.sh"
echo ""
echo "2. To use Cloud SQL with Docker Compose:"
echo "   docker-compose -f docker-compose.yml -f docker-compose.cloud-sql.yml up"
echo ""
echo "3. Connection strings:"
echo "   - Local proxy: postgresql://Admin:Brant01!@localhost:5433/postgres?schema=public"
echo "   - Docker proxy: postgresql://ADMIN:Brant01!@cloud-sql-proxy:5432/postgres?schema=public"
echo ""
echo "4. To test the connection:"
echo "   psql \"postgresql://Admin:Brant01!@localhost:5433/postgres?schema=public\""
echo ""

# Add to .gitignore
if ! grep -q "cloud-sql-proxy-key.json" .gitignore 2>/dev/null; then
    echo "" >> .gitignore
    echo "# Cloud SQL Proxy" >> .gitignore
    echo "cloud-sql-proxy/" >> .gitignore
    echo "cloud-sql-proxy-key.json" >> .gitignore
    echo ".env.cloud-sql" >> .gitignore
    echo "✅ Added Cloud SQL files to .gitignore"
fi