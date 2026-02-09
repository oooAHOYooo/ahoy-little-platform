#!/usr/bin/env bash
# Build SPA (if available) and start Flask on a local port.
set -euo pipefail

cd "$(dirname "$0")/.."

PORT="${PORT:-5002}"

if command -v node >/dev/null 2>&1 && [ -f spa/package.json ]; then
  echo "Building Vue SPA (spa-dist) with VITE_API_BASE=..."
  (cd spa && npm ci && VITE_API_BASE= npm run build)
else
  echo "Node or spa/ not found; skipping SPA build."
fi

echo "Starting Flask on port ${PORT}..."
PORT="${PORT}" python app.py
