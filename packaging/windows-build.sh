#!/bin/bash
# Windows Build Script for Ahoy Indie Media
# Builds Windows EXE and creates installer using NSIS
# Can be run on Windows (via Git Bash/MSYS2) or WSL

set -e

echo "🪟 Building Ahoy Indie Media for Windows..."

# Get absolute paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"
BUILD_DIR="$PROJECT_ROOT/build"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf "$DIST_DIR/AhoyIndieMedia*" "$BUILD_DIR"

# Change to project root
cd "$PROJECT_ROOT"

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Check if required dependencies are installed
echo "📦 Checking dependencies..."
python -c "import webview" 2>/dev/null || {
    echo "📦 Installing pywebview..."
    pip install pywebview
}

# Build Windows executable using PyInstaller spec
echo "🔨 Building Windows EXE with PyInstaller..."
pyinstaller \
    --clean \
    --noconfirm \
    --distpath "$DIST_DIR" \
    --workpath "$BUILD_DIR" \
    --specpath "$PROJECT_ROOT" \
    packaging/ahoy.spec

# Check if build was successful
if [ ! -f "$DIST_DIR/AhoyIndieMedia.exe" ]; then
    echo "❌ Failed to build Windows executable"
    exit 1
fi

EXE_SIZE=$(du -sh "$DIST_DIR/AhoyIndieMedia.exe" 2>/dev/null | cut -f1 || echo "unknown")
echo "✅ Successfully built Windows executable"
echo "📁 EXE path: $DIST_DIR/AhoyIndieMedia.exe"
echo "📏 EXE size: $EXE_SIZE"

# Check if NSIS is available for creating installer
if command -v makensis &> /dev/null || command -v "C:\Program Files (x86)\NSIS\makensis.exe" &> /dev/null; then
    echo "📦 Creating Windows installer with NSIS..."
    
    # Find NSIS executable
    if command -v makensis &> /dev/null; then
        NSIS_CMD="makensis"
    elif [ -f "C:\Program Files (x86)\NSIS\makensis.exe" ]; then
        NSIS_CMD="C:\Program Files (x86)\NSIS\makensis.exe"
    elif [ -f "C:\Program Files\NSIS\makensis.exe" ]; then
        NSIS_CMD="C:\Program Files\NSIS\makensis.exe"
    else
        echo "⚠️  NSIS not found. Skipping installer creation."
        echo "   Download NSIS from: https://nsis.sourceforge.io/"
        echo "   Then run: makensis packaging/windows-installer.nsi"
        exit 0
    fi
    
    # Create installer
    "$NSIS_CMD" /DPROJECT_ROOT="$PROJECT_ROOT" "$SCRIPT_DIR/windows-installer.nsi"
    
    if [ -f "$DIST_DIR/Ahoy Indie Media-Setup.exe" ]; then
        INSTALLER_SIZE=$(du -sh "$DIST_DIR/Ahoy Indie Media-Setup.exe" 2>/dev/null | cut -f1 || echo "unknown")
        echo "✅ Successfully created Windows installer"
        echo "📁 Installer path: $DIST_DIR/Ahoy Indie Media-Setup.exe"
        echo "📏 Installer size: $INSTALLER_SIZE"
    else
        echo "⚠️  Installer creation may have failed. Check NSIS output above."
    fi
else
    echo "⚠️  NSIS not found. Installer not created."
    echo "   To create installer:"
    echo "   1. Download NSIS from: https://nsis.sourceforge.io/"
    echo "   2. Run: makensis packaging/windows-installer.nsi"
    echo "   Or install NSIS and run this script again."
fi

# Calculate SHA256 checksum
echo "🔐 Calculating SHA256 checksum..."
if command -v sha256sum &> /dev/null; then
    sha256sum "$DIST_DIR/AhoyIndieMedia.exe" > "$DIST_DIR/AhoyIndieMedia.exe.sha256" 2>/dev/null || true
elif command -v shasum &> /dev/null; then
    shasum -a 256 "$DIST_DIR/AhoyIndieMedia.exe" > "$DIST_DIR/AhoyIndieMedia.exe.sha256" 2>/dev/null || true
fi

echo "🎉 Windows build complete!"
echo ""
echo "📦 Files created:"
echo "   - $DIST_DIR/AhoyIndieMedia.exe (standalone executable)"
if [ -f "$DIST_DIR/Ahoy Indie Media-Setup.exe" ]; then
    echo "   - $DIST_DIR/Ahoy Indie Media-Setup.exe (installer)"
fi

