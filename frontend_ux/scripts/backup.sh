#!/bin/bash

set -e

# Configuration
BACKUP_DIR="/backups"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-7}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🗄️  Starting database backup..."

# Create backup
pg_dump -h database -U ${POSTGRES_USER} -d ${POSTGRES_DB} > ${BACKUP_DIR}/backup_${TIMESTAMP}.sql

# Compress backup
gzip ${BACKUP_DIR}/backup_${TIMESTAMP}.sql

echo "✅ Backup created: backup_${TIMESTAMP}.sql.gz"

# Clean old backups
find ${BACKUP_DIR} -name "backup_*.sql.gz" -mtime +${RETENTION_DAYS} -delete

echo "🧹 Cleaned backups older than ${RETENTION_DAYS} days"
