#!/usr/bin/env bash
set -euo pipefail

echo "Running database migrations..."
alembic upgrade head

echo "Importing content from legacy JSON into database..."
python scripts/import_content_from_json.py

echo "Importing events and merch (Render-dynamic)..."
python scripts/import_events_merch.py || true

echo "Importing podcast collection (flat list -> DB)..."
python scripts/import_podcast_collection.py || true

echo "Starting gunicorn..."
exec gunicorn app:app --workers 2 --threads 4 --timeout 120


