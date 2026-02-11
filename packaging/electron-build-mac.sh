#!/bin/bash
# Electron macOS Build Script for Ahoy Indie Media
# Builds a macOS .app bundle and .dmg using Electron

set -e

echo "🍎 Building Ahoy Indie Media for macOS with Electron..."

# Get absolute paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js (https://nodejs.org/)"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

# Check if electron-builder is installed
if ! npm list electron-builder &> /dev/null; then
    echo "📦 Installing electron-builder..."
    npm install --save-dev electron-builder
fi

# Ensure Python is available (for Flask server)
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3"
    exit 1
fi

# Check Python dependencies (optional; use venv if you hit externally-managed-environment)
echo "🐍 Checking Python dependencies..."
python3 -c "import flask" 2>/dev/null || {
    echo "⚠️  Flask not found. Install with: pip install -r requirements.txt (or use a venv)"
}

# Ensure desktop_main.py exists
if [ ! -f "desktop_main.py" ]; then
    echo "❌ desktop_main.py not found"
    exit 1
fi

# Build with electron-builder
echo "🔨 Building macOS app with Electron..."
npm run electron:build:mac:dmg

# Check if build was successful
DIST_ELECTRON="$PROJECT_ROOT/dist-electron"
DIST_DOWNLOADS="$PROJECT_ROOT/dist"
if [ -d "$DIST_ELECTRON" ]; then
    echo ""
    echo "✅ Electron build complete!"
    echo "📁 Build artifacts in: $DIST_ELECTRON"
    ls -lh "$DIST_ELECTRON"/*.dmg "$DIST_ELECTRON"/*.app 2>/dev/null || ls -lh "$DIST_ELECTRON"/* 2>/dev/null || true
    # Copy DMG (and .zip) to dist/ so /downloads page can serve them
    mkdir -p "$DIST_DOWNLOADS"
    for f in "$DIST_ELECTRON"/*.dmg "$DIST_ELECTRON"/*.zip 2>/dev/null; do
        [ -e "$f" ] && cp "$f" "$DIST_DOWNLOADS/" && echo "📎 Linked to downloads: $DIST_DOWNLOADS/$(basename "$f")"
    done
    echo ""
    echo "🎉 macOS Electron build successful! DMG is in dist/ and linked from /downloads"
else
    echo "❌ Build directory not found. Build may have failed."
    exit 1
fi

