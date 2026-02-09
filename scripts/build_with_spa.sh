#!/usr/bin/env bash
# Install Python deps and build Vue SPA so Flask can serve it at app.ahoy.ooo.
# On Render: use this as buildCommand so spa-dist exists before gunicorn starts.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "Installing Python dependencies..."
pip install -r requirements.txt

if command -v node >/dev/null 2>&1 && [ -f spa/package.json ]; then
  echo "Building Vue SPA (spa-dist)..."
  (cd spa && npm ci && npm run build)
else
  echo "Node not found or spa/package.json missing; skipping SPA build (web will use server-rendered pages)."
fi
