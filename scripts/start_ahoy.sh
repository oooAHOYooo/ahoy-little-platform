#!/usr/bin/env bash
# Build SPA (if available) and start Flask on a local port.
set -euo pipefail

cd "$(dirname "$0")/.."

PORT="${PORT:-5002}"

if [ -f spa/package.json ]; then
  # Try to load NVM if node is not version 20 or if we want to ensure we use .nvmrc
  export NVM_DIR="$HOME/.nvm"
  # Load nvm from standard locations if it's not already in path
  if ! command -v nvm >/dev/null 2>&1; then
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    [ -s "/usr/local/opt/nvm/nvm.sh" ] && \. "/usr/local/opt/nvm/nvm.sh"
    [ -s "$(brew --prefix nvm)/nvm.sh" ] && \. "$(brew --prefix nvm)/nvm.sh" 2>/dev/null || true
  fi

  if command -v nvm >/dev/null 2>&1; then
    echo "Attempting to use Node version from .nvmrc..."
    nvm use || nvm install
  fi

  if command -v node >/dev/null 2>&1; then
    NODE_VER=$(node -p "process.versions.node.split('.')[0]")
    if [ "${NODE_VER:-0}" -lt 20 ]; then
      echo "Error: Vue SPA build requires Node 20+. Current: $(node -v). Use: nvm use (or install Node 20)."
      exit 1
    fi
    echo "Building Vue SPA (spa-dist) with VITE_API_BASE=..."
    (cd spa && npm install && VITE_API_BASE= npm run build)
  else
    echo "Node not found; skipping SPA build."
  fi
else
  echo "spa/ not found; skipping SPA build."
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
