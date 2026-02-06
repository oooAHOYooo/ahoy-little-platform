#!/usr/bin/env bash
set -euo pipefail

echo "Running database migrations..."
alembic upgrade heads

echo "Importing content from legacy JSON into database..."
python scripts/import_content_from_json.py

echo "Starting gunicorn..."
exec gunicorn app:app --workers 2 --threads 4 --timeout 120


