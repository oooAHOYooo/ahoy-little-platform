#!/usr/bin/env bash
# Build SPA (if available) and start Flask on a local port.
set -euo pipefail

cd "$(dirname "$0")/.."

PORT="${PORT:-5002}"

if command -v node >/dev/null 2>&1 && [ -f spa/package.json ]; then
  NODE_VER=$(node -p "process.versions.node.split('.')[0]")
  if [ "${NODE_VER:-0}" -lt 18 ]; then
    echo "Error: Vue SPA build requires Node 18+. Current: $(node -v). Use: nvm use (or install Node 20)."
    exit 1
  fi
  echo "Building Vue SPA (spa-dist) with VITE_API_BASE=..."
  (cd spa && npm install && VITE_API_BASE= npm run build)
else
  echo "Node or spa/ not found; skipping SPA build."
fi

echo "Running database migrations..."
if [ -d "venv" ]; then
  PYTHONPATH="$(pwd):${PYTHONPATH:-}" ./venv/bin/alembic upgrade heads || true
else
  PYTHONPATH="$(pwd):${PYTHONPATH:-}" alembic upgrade heads || true
fi

echo "Starting Flask on port ${PORT}..."
if [ -d "venv" ]; then
  echo "Using virtual environment found at ./venv"
  PORT="${PORT}" ./venv/bin/python app.py
else
  PORT="${PORT}" python app.py
fi
