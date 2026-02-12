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
  (cd spa && npm ci && VITE_API_BASE= npm run build)
else
  echo "Node or spa/ not found; skipping SPA build."
fi

echo "Starting Flask on port ${PORT}..."
PORT="${PORT}" python app.py
