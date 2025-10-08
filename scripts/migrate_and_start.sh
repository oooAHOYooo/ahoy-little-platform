#!/usr/bin/env bash
set -euo pipefail

echo "Running database migrations..."
alembic upgrade head

echo "Starting gunicorn..."
exec gunicorn app:app --workers 2 --threads 4 --timeout 120


