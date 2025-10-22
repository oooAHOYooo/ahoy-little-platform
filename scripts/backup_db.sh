#!/usr/bin/env bash
"""
Nightly database backup script for Ahoy Indie Media
Backs up PostgreSQL database and uploads to cloud storage
"""

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting database backup...${NC}"

# Get database URL from environment
DATABASE_URL="${DATABASE_URL:-}"
if [[ -z "$DATABASE_URL" ]]; then
    echo -e "${RED}Error: DATABASE_URL environment variable not set${NC}"
    exit 1
fi

# Parse database URL
# Format: postgresql://user:password@host:port/database
if [[ "$DATABASE_URL" =~ postgresql://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then
    DB_USER="${BASH_REMATCH[1]}"
    DB_PASSWORD="${BASH_REMATCH[2]}"
    DB_HOST="${BASH_REMATCH[3]}"
    DB_PORT="${BASH_REMATCH[4]}"
    DB_NAME="${BASH_REMATCH[5]}"
else
    echo -e "${RED}Error: Invalid DATABASE_URL format${NC}"
    exit 1
fi

# Set PGPASSWORD for pg_dump
export PGPASSWORD="$DB_PASSWORD"

# Generate timestamp and filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILENAME="ahoy_backup_${TIMESTAMP}.sql"
BACKUP_PATH="/tmp/${BACKUP_FILENAME}"
COMPRESSED_FILENAME="${BACKUP_FILENAME}.gz"
COMPRESSED_PATH="/tmp/${COMPRESSED_FILENAME}"

echo -e "${GREEN}Backing up database: ${DB_NAME}@${DB_HOST}:${DB_PORT}${NC}"

# Create database dump
pg_dump \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --username="$DB_USER" \
    --dbname="$DB_NAME" \
    --verbose \
    --no-password \
    --format=plain \
    --file="$BACKUP_PATH"

# Compress the backup
echo -e "${GREEN}Compressing backup...${NC}"
gzip "$BACKUP_PATH"
mv "$BACKUP_PATH.gz" "$COMPRESSED_PATH"

# Get file size and checksum
FILE_SIZE=$(stat -f%z "$COMPRESSED_PATH" 2>/dev/null || stat -c%s "$COMPRESSED_PATH" 2>/dev/null || echo "unknown")
CHECKSUM=$(shasum -a 256 "$COMPRESSED_PATH" | cut -d' ' -f1)

echo -e "${GREEN}Backup created: ${COMPRESSED_FILENAME} (${FILE_SIZE} bytes)${NC}"
echo -e "${GREEN}Checksum: ${CHECKSUM}${NC}"

# Upload to cloud storage
UPLOAD_SUCCESS=false

# Try AWS S3 first
if [[ -n "${AWS_ACCESS_KEY_ID:-}" && -n "${AWS_SECRET_ACCESS_KEY:-}" && -n "${S3_BUCKET:-}" ]]; then
    echo -e "${GREEN}Uploading to AWS S3...${NC}"
    if aws s3 cp "$COMPRESSED_PATH" "s3://${S3_BUCKET}/backups/${COMPRESSED_FILENAME}"; then
        echo -e "${GREEN}✅ Uploaded to S3: s3://${S3_BUCKET}/backups/${COMPRESSED_FILENAME}${NC}"
        UPLOAD_SUCCESS=true
    else
        echo -e "${YELLOW}⚠️ S3 upload failed${NC}"
    fi
fi

# Try Google Cloud Storage if S3 failed
if [[ "$UPLOAD_SUCCESS" == "false" && -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" && -n "${GCS_BUCKET:-}" ]]; then
    echo -e "${GREEN}Uploading to Google Cloud Storage...${NC}"
    if gsutil cp "$COMPRESSED_PATH" "gs://${GCS_BUCKET}/backups/${COMPRESSED_FILENAME}"; then
        echo -e "${GREEN}✅ Uploaded to GCS: gs://${GCS_BUCKET}/backups/${COMPRESSED_FILENAME}${NC}"
        UPLOAD_SUCCESS=true
    else
        echo -e "${YELLOW}⚠️ GCS upload failed${NC}"
    fi
fi

# Clean up local file
rm -f "$COMPRESSED_PATH"

# Generate JSON summary
cat << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "database": "$DB_NAME",
  "backup_file": "$COMPRESSED_FILENAME",
  "file_size_bytes": $FILE_SIZE,
  "checksum_sha256": "$CHECKSUM",
  "upload_success": $UPLOAD_SUCCESS,
  "retention_days": 30
}
EOF

if [[ "$UPLOAD_SUCCESS" == "true" ]]; then
    echo -e "${GREEN}✅ Backup completed successfully${NC}"
    exit 0
else
    echo -e "${RED}❌ Backup created but upload failed${NC}"
    exit 1
fi
